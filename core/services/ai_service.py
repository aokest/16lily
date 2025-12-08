import json
import urllib.request
import urllib.error
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import AIConfiguration, Customer, PromptTemplate

class AIService:
    def __init__(self, config_id=None):
        if config_id:
            try:
                self.config = AIConfiguration.objects.get(pk=config_id)
            except AIConfiguration.DoesNotExist:
                self.config = AIConfiguration.objects.filter(is_active=True).first()
        else:
            self.config = AIConfiguration.objects.filter(is_active=True).first()
        
    def _get_client(self):
        if not self.config:
            return None, "No active AI configuration found."
        return self.config, None

    def _get_prompt(self, scene, default_content=""):
        """
        Retrieve the active prompt template for a specific scene.
        If not found, return the default content.
        """
        template = PromptTemplate.objects.filter(scene=scene, is_active=True).order_by('-updated_at').first()
        if template:
            return template.template
        return default_content

    def _call_llm_json(self, prompt, user_text):
        if not user_text: return None
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text}
        ]
        
        # --- 1. Ollama Call ---
        if self.config.provider == AIConfiguration.Provider.OLLAMA:
            import requests
            # Special handling for Ollama because 'requests' to localhost often fail inside Docker
            # Try host.docker.internal first if in Docker, else localhost
            
            # Note: self.config.base_url usually is http://127.0.0.1:11434/v1 or similar
            # But the user might have set it to localhost which fails in Docker
            
            api_url = f"{self.config.base_url}/chat/completions"
            headers = {"Content-Type": "application/json"}
            payload = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": 0.1,
                "stream": False,
                "format": "json" # Ollama supports json mode natively
            }
            
            print(f"DEBUG: Calling Ollama at {api_url} with model {self.config.model_name}")
            
            try:
                response = requests.post(api_url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content']
                return self._clean_and_parse_json(content)
            except Exception as e:
                # If host.docker.internal failed (running locally), try localhost fallback
                if 'host.docker.internal' in api_url:
                    print("DEBUG: Retrying with localhost (host.docker.internal failed)...")
                    try:
                        fallback_url = api_url.replace("host.docker.internal", "127.0.0.1")
                        response = requests.post(fallback_url, json=payload, headers=headers, timeout=30)
                        response.raise_for_status()
                        result = response.json()
                        content = result['choices'][0]['message']['content']
                        return self._clean_and_parse_json(content)
                    except:
                        pass # Fallback failed too

                # If localhost failed, try host.docker.internal fallback just in case (running in docker)
                if '127.0.0.1' in api_url or 'localhost' in api_url:
                    print("DEBUG: Retrying with host.docker.internal...")
                    try:
                        fallback_url = api_url.replace("127.0.0.1", "host.docker.internal").replace("localhost", "host.docker.internal")
                        response = requests.post(fallback_url, json=payload, headers=headers, timeout=30)
                        response.raise_for_status()
                        result = response.json()
                        content = result['choices'][0]['message']['content']
                        return self._clean_and_parse_json(content)
                    except:
                        pass # Fallback failed too
                
                print(f"LLM Connection Error: {e}")
                return {'error': f"Connection Failed to {self.config.base_url}: {str(e)}"}

        # --- 2. OpenAI-Compatible Call (DeepSeek, Moonshot, OpenAI) ---
        else:
            import openai
            client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
            
            try:
                print(f"DEBUG: Calling OpenAI-compatible API at {self.config.base_url} model={self.config.model_name}")
                completion = client.chat.completions.create(
                    model=self.config.model_name,
                    messages=messages,
                    temperature=0.1,
                    response_format={"type": "json_object"}  # Most new APIs support this
                )
                content = completion.choices[0].message.content
                return self._clean_and_parse_json(content)
            except Exception as e:
                print(f"LLM API Error: {e}")
                return {'error': f"API Error ({self.config.provider}): {str(e)}"}
                
    def _clean_and_parse_json(self, content):
        # --- Enhanced JSON Cleaning for smaller models (like Qwen 8b) ---
        content = content.strip()
        # Remove Markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        # Locate the first '{' and last '}' to handle "Here is the JSON:" prefix
        first_brace = content.find('{')
        last_brace = content.rfind('}')
        if first_brace != -1 and last_brace != -1:
            content = content[first_brace:last_brace+1]
        
        # Try to clean up potential trailing commas or bad chars if parse fails
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error. Raw content: {content}")
            return {"error": f"Failed to parse JSON: {str(e)}", "raw": content}

    def find_user_id(self, name_str):
        if not name_str: return None
        user = User.objects.filter(username=name_str).first()
        if user: return user.id
        for u in User.objects.all():
            full_name = f"{u.last_name}{u.first_name}"
            if full_name == name_str: return u.id
            if u.first_name == name_str: return u.id
        return None

    def find_customer_id(self, name_str):
        if not name_str: return None
        customer = Customer.objects.filter(name__icontains=name_str).first()
        if customer: return customer.id
        return None

    # --- Specific Parsing Functions ---

    def parse_opportunity(self, text):
        default_prompt = """
        You are a smart data extraction assistant.
        Extract Sales Opportunity info from the user's text and return strictly valid JSON.
        
        Required JSON keys:
        - name: Opportunity Name (Summarize "Customer + Product/Service", in Simplified Chinese).
        - amount: Estimated amount (number only, e.g. 150000).
        - customer_name: Customer company name (in Simplified Chinese).
        - customer_contact_name: Contact person name.
        - sales_manager_name: Sales person name (e.g. "付磊").
        - project_manager_name: Project manager name (e.g. "张三").
        - expected_sign_date: YYYY-MM-DD.
        - stage: One of [CONTACT, REQ_ANALYSIS, INITIATION, BIDDING, DELIVERY, AFTER_SALES, COMPLETED].
        - win_rate: Integer 0-100 (Probability).
        - competitors: String, comma separated.
        - source: String (e.g. "Old Customer", "Tender").
        - product_line: String (e.g. "Network Range", "City Safety").
        - customer_industry: String (e.g. "Education", "Finance").
        - customer_region: String (e.g. "Beijing", "North China").
        - description: A detailed summary of the opportunity background and needs.
        
        Infer defaults if missing:
        - stage: 'CONTACT'
        - amount: 0
        - expected_sign_date: End of current month (YYYY-MM-DD)

        Example:
        Input: "九号电动车商机，15万，销售员付磊"
        Output: {"name": "九号电动车-商机", "amount": 150000, "customer_name": "九号电动车", "sales_manager_name": "付磊", "expected_sign_date": "2025-12-31", "stage": "CONTACT"}
        """
        prompt = self._get_prompt(PromptTemplate.Scene.OPPORTUNITY, default_prompt)
        prompt += f"\nCurrent Date: {timezone.now().strftime('%Y-%m-%d')}"
        
        data = self._call_llm_json(prompt, text)
        if not data: return {'error': 'AI returned no data'}
        if 'error' in data: return data
        
        sales_manager_id = self.find_user_id(data.get('sales_manager_name'))
        customer_id = self.find_customer_id(data.get('customer_name'))
        
        return {
            'name': data.get('name'),
            'amount': data.get('amount'),
            'customer_name': data.get('customer_name'),
            'customer': customer_id,
            'customer_contact_name': data.get('customer_contact_name'),
            'sales_manager': sales_manager_id,
            'expected_sign_date': data.get('expected_sign_date'),
            'stage': data.get('stage') or 'CONTACT',
            'win_rate': data.get('win_rate'),
            'competitors': data.get('competitors'),
            'source': data.get('source'),
            'product_line': data.get('product_line'),
            'customer_industry': data.get('customer_industry'),
            'customer_region': data.get('customer_region'),
            'description': data.get('description'),
            # Note: project_manager logic is complex if user doesn't exist, so frontend will handle name display for now
            'project_manager_name': data.get('project_manager_name'),
        }

    def parse_todo_task(self, text):
        default_prompt = """
        Analyze the user's text and extract a Todo Task.
        Output JSON keys:
        - title: A short, concise summary (max 10 words).
        - description: The full detailed description.
        - deadline: YYYY-MM-DD HH:MM:SS (Calculate based on current date/time if relative terms like "tomorrow" are used).
        - assignee_name: The name of the person assigned to this task (if mentioned).
        """
        prompt = self._get_prompt(PromptTemplate.Scene.TODO, default_prompt)
        prompt += f"\nCurrent Date/Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        data = self._call_llm_json(prompt, text)
        if not data: return {'error': 'AI returned no data'}
        if 'error' in data: return data
        
        return {
            'title': data.get('title'),
            'description': data.get('description'),
            'deadline': data.get('deadline'),
            'assignee': self.find_user_id(data.get('assignee_name'))
        }

    def parse_work_report(self, text):
        default_prompt = """
        Generate a structured Work Report based on the user's rough input.
        Language: Simplified Chinese (简体中文).
        
        Output JSON keys:
        - content: A well-formatted report (Markdown supported) with sections like '今日工作', '进度', '下一步计划'.
        - ai_summary: A one-sentence summary (in Chinese).
        - report_type: One of [DAILY, WEEKLY, MONTHLY] (Infer from context, default DAILY).
        - related_projects: A list of project names or keywords mentioned.
        - next_steps: A list of suggested next steps.
        """
        prompt = self._get_prompt(PromptTemplate.Scene.REPORT, default_prompt)
        
        data = self._call_llm_json(prompt, text)
        return data

    def parse_competition(self, text):
        default_prompt = """
        Extract Competition info.
        Output JSON keys:
        - name: Competition Name.
        - time: Start Date (YYYY-MM-DD).
        - location: Location.
        - type: Type of competition.
        - owner_name: Person in charge.
        """
        prompt = self._get_prompt(PromptTemplate.Scene.COMPETITION, default_prompt)
        prompt += f"\nCurrent Date: {timezone.now().strftime('%Y-%m-%d')}"
        
        data = self._call_llm_json(prompt, text)
        return data
        
    def parse_market_activity(self, text):
        default_prompt = """
        Extract Market Activity info.
        Output JSON keys:
        - name: Activity Name.
        - time: Date (YYYY-MM-DD).
        - location: Location.
        - type: Type (e.g. Salon, Exhibition).
        """
        prompt = self._get_prompt(PromptTemplate.Scene.MARKET, default_prompt)
        prompt += f"\nCurrent Date: {timezone.now().strftime('%Y-%m-%d')}"
        
        data = self._call_llm_json(prompt, text)
        return data

    def parse_customer(self, text):
        default_prompt = """
        Extract Customer Company info.
        Output JSON keys:
        - name: Company Name.
        - industry: Industry.
        - scale: One of [SMALL, MEDIUM, LARGE, ENTERPRISE, GOV].
        - legal_representative: Legal Rep Name.
        - website: URL.
        """
        prompt = self._get_prompt(PromptTemplate.Scene.CUSTOMER, default_prompt)
        data = self._call_llm_json(prompt, text)
        return data
        
    def parse_contact(self, text):
        prompt = """
        Extract Contact Person info.
        Output JSON keys:
        - name: Name.
        - title: Job Title.
        - phone: Phone Number.
        - email: Email.
        - customer_name: Company Name they belong to.
        """
        # No dedicated scene for contact yet, use default or maybe OTHER
        data = self._call_llm_json(prompt, text)
        return data
