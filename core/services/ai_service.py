import json
import urllib.request
import urllib.error
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import AIConfiguration, Customer, PromptTemplate, SubmissionLog

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

    def _call_llm_json(self, prompt, user_text, user=None, intent=None, entity=None):
        """
        调用LLM并期望返回JSON：
        - 自动适配 Ollama 原生API(`/api/chat`)与 OpenAI兼容API(`/v1/chat/completions`)
        - 对返回内容进行JSON清洗与解析
        - 记录原始返回到 SubmissionLog (如果提供了 user)
        """
        if not user_text: return None
        if not self.config:
            return {'error': 'No active AI model configured'}
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_text}
        ]
        
        raw_content = ""
        error_msg = ""
        
        try:
            # --- 1. Ollama Call ---
            if self.config.provider == AIConfiguration.Provider.OLLAMA:
                import requests
                
                # 获取配置的基础地址
                base_url = self.config.base_url or 'http://localhost:11434'
                
                # 自动处理 Docker 内部访问宿主机的问题
                # 如果在 Docker 中运行，localhost 会指向容器自身，需要换成 host.docker.internal
                import os
                is_docker = os.path.exists('/.dockerenv')
                if is_docker:
                    base_url = base_url.replace('localhost', 'host.docker.internal').replace('127.0.0.1', 'host.docker.internal')
                
                # 选择API路径：如果base_url包含/v1则使用openai兼容接口，否则使用Ollama原生接口
                use_openai_compat = '/v1' in base_url
                api_url = f"{base_url}/chat/completions" if use_openai_compat else f"{base_url}/api/chat"
                
                headers = {"Content-Type": "application/json"}
                # 两种接口负载格式
                if use_openai_compat:
                    payload = {
                        "model": self.config.model_name,
                        "messages": messages,
                        "temperature": 0.1,
                        "stream": False,
                        "format": "json"
                    }
                else:
                    payload = {
                        "model": self.config.model_name,
                        "messages": messages,
                        "options": {"temperature": 0.1},
                        "stream": False,
                        "format": "json"
                    }
                
                print(f"DEBUG: Calling Ollama at {api_url} with model {self.config.model_name}")
                
                try:
                    response = requests.post(api_url, json=payload, headers=headers, timeout=60)
                    response.raise_for_status()
                    result = response.json()
                    # 解析两种返回结构
                    if use_openai_compat:
                        raw_content = result['choices'][0]['message']['content']
                    else:
                        # 原生 /api/chat 返回 {"message":{"role":"assistant","content":"..."},"done":true,...}
                        raw_content = (result.get('message') or {}).get('content') or ''
                except requests.exceptions.ConnectionError:
                    error_msg = f"无法连接到 AI 服务 ({api_url})。请确认 Ollama 是否正在运行。如果在 Docker 中运行，请确保配置了 host.docker.internal。"
                    print(f"LLM Connection Error: {error_msg}")
                    return {'error': error_msg}
                except Exception as e:
                    error_msg = f"AI 服务调用出错: {str(e)}"
                    print(f"LLM Error: {error_msg}")
                    return {'error': error_msg}

            # --- 2. OpenAI-Compatible Call (DeepSeek, Moonshot, OpenAI) ---
            else:
                import openai
                if not self.config.api_key and not self.config.base_url:
                    error_msg = 'API credentials missing for selected provider'
                else:
                    client = openai.OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
                    
                    try:
                        print(f"DEBUG: Calling OpenAI-compatible API at {self.config.base_url} model={self.config.model_name}")
                        completion = client.chat.completions.create(
                            model=self.config.model_name,
                            messages=messages,
                            temperature=0.1,
                            response_format={"type": "json_object"}  # Attempt strict JSON
                        )
                        raw_content = completion.choices[0].message.content
                        
                        # Check if it looks like JSON
                        if not raw_content.strip().startswith('{') and not raw_content.strip().startswith('```'):
                             # If failed, retry with stricter prompt
                            strict_messages = [
                                {"role": "system", "content": "You MUST return a valid JSON object. No markdown, no explanations."},
                                {"role": "user", "content": user_text}
                            ]
                            completion2 = client.chat.completions.create(
                                model=self.config.model_name,
                                messages=strict_messages,
                                temperature=0.0,
                                response_format={"type": "json_object"}
                            )
                            raw_content = completion2.choices[0].message.content
                    except Exception as e:
                        print(f"LLM API Error: {e}")
                        error_msg = f"API Error: {str(e)}"
        
        except Exception as global_e:
             print(f"Global LLM Error: {global_e}")
             error_msg = f"Global Error: {str(global_e)}"

        # Parse
        parsed = {}
        if not error_msg:
             parsed = self._clean_and_parse_json(raw_content)
        else:
             parsed = {'error': error_msg}
        
        # Log to DB if user provided
        if user:
            print(f"DEBUG: Attempting to log submission for user {user.username}")
            try:
                status = SubmissionLog.Status.FAILED if ('error' in parsed) else SubmissionLog.Status.PARSED
                err = parsed.get('error', '') if isinstance(parsed, dict) else ''
                if error_msg: err += f" | {error_msg}"
                
                SubmissionLog.objects.create(
                    user=user,
                    status=status,
                    text_input=user_text,
                    prompt=prompt,
                    raw_response=raw_content,
                    error_message=err,
                    intent=intent or '',
                    entity=entity or '',
                    result_payload=parsed
                )
                print("DEBUG: SubmissionLog created successfully")
            except Exception as log_e:
                print(f"Failed to save SubmissionLog: {log_e}")
                import traceback
                traceback.print_exc()
                
        return parsed

    def _clean_and_parse_json(self, content):
        # --- Enhanced JSON Cleaning ---
        if not content: return {'error': 'Empty response from LLM'}
        content = content.strip()
        
        # Remove Markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        # 1. Try standard JSON load
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
            
        # 2. Try to find the first valid JSON object by brace counting
        # This handles cases like: "Here is the JSON: { ... } Hope it helps."
        # and cases with nested braces.
        try:
            extracted = self._extract_json_by_braces(content)
            if extracted:
                return json.loads(extracted)
        except Exception:
            pass

        # 3. Fallback: regex search for { ... } (greedy)
        import re
        m = re.search(r'\{[\s\S]*\}', content)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass

        print(f"JSON Decode Error. Raw content: {content}")
        return {"error": "Failed to parse JSON", "raw": content}

    def _extract_json_by_braces(self, text):
        """
        Extract the first valid JSON object string by counting braces.
        """
        stack = []
        start_index = -1
        
        for i, char in enumerate(text):
            if char == '{':
                if not stack:
                    start_index = i
                stack.append('{')
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack:
                        # Found a complete JSON object
                        return text[start_index:i+1]
        return None

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

    def parse_opportunity(self, text, user=None):
        default_prompt = """
        You are a smart data extraction assistant.
        Extract Sales Opportunity info from the user's text and return strictly valid JSON.
        
        Required JSON keys:
        - name: Opportunity Name (Summarize "Customer + Product/Service", in Simplified Chinese).
        - amount: Estimated amount (number only, e.g. 150000).
        - customer_name: Customer company name (in Simplified Chinese).
        - customer_code: Customer code (e.g. "CUST-001", "XM-002").
        - customer_contact_name: Contact person name.
        - customer_phone: Contact phone number.
        - customer_email: Contact email.
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
        template = PromptTemplate.objects.filter(scene=PromptTemplate.Scene.OPPORTUNITY, is_active=True).order_by('-updated_at').first()
        if template:
            if 'customer_code' not in template.template:
                template.template = default_prompt
                template.save()
            prompt = template.template
        else:
            PromptTemplate.objects.create(
                name="Standard Opportunity Prompt V2",
                scene=PromptTemplate.Scene.OPPORTUNITY,
                template=default_prompt,
                is_active=True
            )
            prompt = default_prompt

        prompt += f"\nCurrent Date: {timezone.now().strftime('%Y-%m-%d')}"
        
        data = self._call_llm_json(prompt, text, user=user, intent='create', entity='opportunity')
        
        if not data or ('error' in data):
            # Local fallback extraction
            t = text or ''
            import re
            cust = None
            m = re.search(r'客户名称[:：]\s*([^\s，,。;；]+)', t) or re.search(r'新增(?:一个|一条|一项)?([^\s，,。;；]{2,40})的商机', t) or re.search(r'([^\s，,。;；]{2,40})商机', t)
            if m: cust = m.group(1).strip()
            amt = 0
            m_amt = re.search(r'(预算|金额)\s*([0-9]+(?:\.[0-9]+)?)\s*(千|万|百万|亿)?', t)
            if m_amt:
                num = float(m_amt.group(2)); unit = (m_amt.group(3) or '')
                unit_map = {'千': 1_000, '万': 10_000, '百万': 1_000_000, '亿': 100_000_000}
                amt = int(num * unit_map.get(unit, 1))
            exp = None
            m_q = re.search(r'明年?\s*Q([1-4])', t, re.IGNORECASE) or re.search(r'Q([1-4])', t, re.IGNORECASE)
            if m_q:
                q = int(m_q.group(1)); now = timezone.now()
                year = now.year + (1 if '明年' in t else 0)
                middle_month = {1:2,2:5,3:8,4:11}[q]
                exp = f"{year}-{middle_month:02d}-15"
            stage = 'CONTACT'
            if '演示' in t: stage = 'DEMO'
            elif '方案' in t: stage = 'PROPOSAL'
            elif '谈判' in t: stage = 'NEGOTIATION'
            elif '临门' in t or '签约' in t: stage = 'CLOSING'
            reg = None
            m_reg = re.search(r'区域[:：]\s*([^\s，,]+)', t)
            if m_reg: reg = m_reg.group(1).strip()
            else:
                m_loc = re.search(r'在([^\s，,]{1,10})', t)
                if m_loc: reg = m_loc.group(1).strip()
            sales_name = None
            m_sales = re.search(r'销售([^\s，,]{2,10})', t)
            if m_sales: sales_name = m_sales.group(1).strip()
            sales_manager_id = self.find_user_id(sales_name)
            customer_id = self.find_customer_id(cust)
            name = f"{cust}-咨询比赛与演武场" if cust else "咨询比赛与演武场"
            
            fallback_data = {
                'name': name,
                'amount': amt,
                'customer_name': cust,
                'customer': customer_id,
                'sales_manager': sales_manager_id,
                'expected_sign_date': exp,
                'stage': stage,
                'customer_region': reg,
                'description': t
            }
            # Return fallback data but preserve error info if caller needs it
            if data and 'error' in data:
                fallback_data['error'] = data['error']
            return fallback_data
        
        sales_manager_id = self.find_user_id(data.get('sales_manager_name'))
        customer_id = self.find_customer_id(data.get('customer_name'))
        
        return {
            'name': data.get('name'),
            'amount': data.get('amount'),
            'customer_name': data.get('customer_name'),
            'customer_code': data.get('customer_code'),
            'customer': customer_id,
            'customer_contact_name': data.get('customer_contact_name'),
            'customer_phone': data.get('customer_phone'),
            'customer_email': data.get('customer_email'),
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
            'project_manager_name': data.get('project_manager_name'),
        }

    def parse_todo_task(self, text, user=None):
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
        
        data = self._call_llm_json(prompt, text, user=user, intent='create', entity='todo')
        if not data: return {'error': 'AI returned no data'}
        if 'error' in data: return data
        
        return {
            'title': data.get('title'),
            'description': data.get('description'),
            'deadline': data.get('deadline'),
            'assignee': self.find_user_id(data.get('assignee_name'))
        }

    def generate_daily_report(self, user_content, user=None):
        default_prompt = """
        你是一个专业的商务日报生成助手。
        请根据用户提供的“工作要点”或“关键词”，扩写生成一份结构清晰、语言专业的日报。
        
        要求返回严格的 JSON 格式：
        {
            "title": "简短有力的日报标题",
            "content": "分点阐述的详细日报内容，包含今日工作、遇到的问题、明日计划等，Markdown格式"
        }
        
        如果用户输入太少，请合理推断并扩充。
        请保持语气专业、积极。
        """
        prompt = self._get_prompt('daily_report_generation', default_prompt)
        prompt += f"\nCurrent Date: {timezone.now().strftime('%Y-%m-%d')}"
        return self._call_llm_json(prompt, user_content, user=user, intent='generate_daily_report', entity='daily_report')

    def polish_daily_report(self, text, user=None, projects=None):
        """
        润色日报内容，使其更偏向研发、生产、经营结果的总结。
        根据用户角色自动匹配不同的润色风格。
        """
        project_context = ""
        if projects:
            project_names = [p.name for p in projects]
            project_context = f"关联项目: {', '.join(project_names)}"
        
        user_context = ""
        user_role = 'GENERAL'
        
        if user:
            name = f"{user.last_name}{user.first_name}".strip()
            user_context = f"汇报人: {name if name else user.username}"
            
            # 尝试获取用户角色以适配Prompt
            if hasattr(user, 'profile') and user.profile:
                # 假设 profile.job_category 存储了 RND, SALES, MANAGEMENT 等
                # 或者通过 job_title 获取
                cat = user.profile.job_category
                if cat in ['RND', 'RESEARCHER', 'LAB', 'POC', 'DESIGN']:
                    user_role = 'RND'
                elif cat in ['SALES', 'MARKETING']:
                    user_role = 'SALES'
                elif cat in ['MANAGEMENT', 'VP', 'PRESIDENT']:
                    user_role = 'MANAGEMENT'
        
        # --- 定义场景化 Prompts ---
        
        # 1. 研发/技术类
        prompt_rnd = """
        你是一名资深研发技术总监。请将用户的日报润色为专业的技术工作汇报。
        
        【目标风格】
        1. **技术驱动**：使用准确的计算机与软件工程术语（如：重构、迭代、解耦、高并发、延迟优化等）。
        2. **结果导向**：不要只说“做了什么”，要强调“解决了什么问题”或“提升了什么性能”。
        3. **结构化**：
           - **今日产出**：列出具体完成的功能点或修复的Bug。
           - **技术难点**：简述遇到的挑战及解决方案。
           - **明日计划**：明确下一步的开发重点。
        
        【必须执行】
        - 即使原文很简单，也要扩充为标准的技术汇报格式。
        - 去除“今天”、“然后”等口语化词汇。
        - 自动纠正错别字。
        """

        # 2. 销售/市场类
        prompt_sales = """
        你是一名资深销售总监。请将用户的日报润色为结果导向的销售业绩汇报。
        
        【目标风格】
        1. **狼性与进取**：强调商机推进、客户触达和回款进度。
        2. **量化指标**：如果原文包含数字，请重点突出；如果没有，请通过专业话术体现工作量。
        3. **结构化**：
           - **客户跟进**：拜访/沟通情况，明确客户意向度。
           - **商机进展**：项目的阶段变化及下一步赢单策略。
           - **需要支持**：明确所需的资源或协助。
        
        【必须执行】
        - 将“联系了客户”改为“深度触达客户关键决策人”等专业表述。
        - 语气要积极自信。
        """

        # 3. 管理/综合类
        prompt_mgmt = """
        你是一名企业高管。请将用户的日报润色为宏观的管理工作汇报。
        
        【目标风格】
        1. **全局视野**：关注团队进度、资源协调、风险预警。
        2. **价值交付**：强调项目里程碑的达成和业务价值的实现。
        3. **结构化**：
           - **重点进展**：关键项目的里程碑状态。
           - **管理动作**：团队建设、协调沟通、决策事项。
           - **风险与应对**：潜在风险及应对预案。
        """

        # 4. 通用/职能类
        prompt_general = """
        你是专业的企业工作汇报助手。请根据用户提供的原始日报内容，对其进行润色和优化。

        【目标风格】
        1. **语言专业**：简练、严谨，符合企业正式公文规范。
        2. **实质性**：重点突出“工作产出”和“经营结果”。
        3. **转化**：将流水账式的描述转化为结果导向的陈述（例如将“做了X”改为“完成了X，实现了Y效果”）。
        4. **修正**：自动纠正错别字和语病。
        """

        # 选择 Prompt
        selected_prompt = prompt_general
        if user_role == 'RND':
            selected_prompt = prompt_rnd
        elif user_role == 'SALES':
            selected_prompt = prompt_sales
        elif user_role == 'MANAGEMENT':
            selected_prompt = prompt_mgmt

        # 叠加通用 JSON 要求
        json_instruction = """
        【输出要求】
        1. 请返回严格的 JSON 格式，包含一个字段 "content"，其值为润色后的文本内容。
        2. 不要包含任何开场白或解释性语言（如“好的，这是润色后的内容...”）。
        3. Markdown 格式：在 "content" 文本中，请使用 Markdown 语法（如 **加粗**，- 列表）来排版。
        """

        final_default_prompt = selected_prompt + "\n" + json_instruction

        # 尝试从数据库获取模板
        # 根据角色使用不同的 Scene Key，避免通用模板覆盖专用逻辑
        scene_key = PromptTemplate.Scene.REPORT
        if user_role == 'RND':
            scene_key = 'REPORT_RND'
        elif user_role == 'SALES':
            scene_key = 'REPORT_SALES'
        elif user_role == 'MANAGEMENT':
            scene_key = 'REPORT_MANAGEMENT'

        prompt = self._get_prompt(scene_key, final_default_prompt)
        
        # 组装最终上下文
        full_prompt = prompt + f"\n\n{user_context}\n{project_context}\n\n当前日期: {timezone.now().strftime('%Y-%m-%d')}"
        
        # 强制 JSON 约束 (再次强调，防止 Template 没写)
        full_prompt += "\n\nIMPORTANT: You MUST return a valid JSON object with a single key 'content'."

        print(f"DEBUG: Polishing with User Role: {user_role}")
        
        data = self._call_llm_json(full_prompt, text, user=user, intent='polish', entity='daily_report')
        
        if data and isinstance(data, dict) and 'content' in data:
            return data['content']
        
        if data and isinstance(data, dict) and 'error' in data:
            print(f"AI Polish Error: {data['error']}")
        
        return text

    def parse_work_report(self, text, user=None):
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
        
        data = self._call_llm_json(prompt, text, user=user, intent='create', entity='report')
        return data

    def parse_competition(self, text, user=None):
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
        
        data = self._call_llm_json(prompt, text, user=user, intent='create', entity='competition')
        if not data or ('error' in data):
            # Local fallback
            import re, datetime
            t = text or ''
            name = None
            m_name = re.search(r'赛事名称[:：]\s*([^\s，,。;；]+)', t) or re.search(r'新建(?:一个|一项)?([^\s，,。;；]{2,40})', t)
            if m_name: name = m_name.group(1).strip()
            loc = None
            m_loc = re.search(r'地点[:：]\s*([^\s，,。;；]+)', t) or re.search(r'在([^\s，,。;；]{1,10})', t)
            if m_loc: loc = m_loc.group(1).strip()
            ty = None
            m_ty = re.search(r'类型[:：]\s*([^\s，,。;；]+)', t)
            if m_ty: ty = m_ty.group(1).strip()
            now = timezone.now()
            year = now.year + (1 if '明年' in t else 0)
            start = None
            m_q = re.search(r'Q([1-4])', t, re.IGNORECASE)
            if m_q:
                q = int(m_q.group(1)); middle_month = {1:2,2:5,3:8,4:11}[q]
                start = f"{year}-{middle_month:02d}-15"
            else:
                m_m = re.search(r'(\d{1,2})月(上旬|中旬|下旬)', t)
                if m_m:
                    month = int(m_m.group(1)); day_map = {'上旬':5,'中旬':15,'下旬':25}
                    start = datetime.date(year, month, day_map[m_m.group(2)]).isoformat()
            fallback = {'name': name, 'time': start, 'location': loc, 'type': ty}
            if data and 'error' in data: fallback['error'] = data['error']
            return fallback
        return data
        
    def parse_market_activity(self, text, user=None):
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
        
        data = self._call_llm_json(prompt, text, user=user, intent='create', entity='activity')
        if not data or ('error' in data):
            import re, datetime
            t = text or ''
            name = None
            m_name = re.search(r'活动名称[:：]\s*([^\s，,。;；]+)', t) or re.search(r'新建(?:一个|一项)?([^\s，,。;；]{2,40})', t)
            if m_name: name = m_name.group(1).strip()
            loc = None
            m_loc = re.search(r'地点[:：]\s*([^\s，,。;；]+)', t) or re.search(r'在([^\s，,。;；]{1,10})', t)
            if m_loc: loc = m_loc.group(1).strip()
            ty = None
            m_ty = re.search(r'类型[:：]\s*([^\s，,。;；]+)', t)
            if m_ty: ty = m_ty.group(1).strip()
            now = timezone.now(); year = now.year + (1 if '明年' in t else 0)
            dt = None
            m_m = re.search(r'(\d{1,2})月(上旬|中旬|下旬)', t)
            if m_m:
                month = int(m_m.group(1)); day_map = {'上旬':5,'中旬':15,'下旬':25}
                dt = datetime.date(year, month, day_map[m_m.group(2)]).isoformat()
            fallback = {'name': name, 'time': dt, 'location': loc, 'type': ty}
            if data and 'error' in data: fallback['error'] = data['error']
            return fallback
        return data

    def _call_llm(self, prompt, user_text, history=None, **kwargs):
        """
        Legacy/Alias for _call_llm_json for backward compatibility
        or simple text-based calls.
        """
        if not self.config:
             return "Error: No active AI configuration found."
             
        messages = [
            {"role": "system", "content": prompt},
        ]
        
        # Append history if provided (simple concatenation for context)
        if history and isinstance(history, list):
            for h in history:
                role = h.get('role', 'user')
                content = h.get('content', '')
                if content:
                    messages.append({"role": role, "content": content})
                    
        messages.append({"role": "user", "content": user_text})
        
        try:
            if self.config.provider == AIConfiguration.Provider.OLLAMA:
                import requests
                base_url = self.config.base_url or 'http://localhost:11434'
                
                # Docker fix
                import os
                if os.path.exists('/.dockerenv'):
                     base_url = base_url.replace('localhost', 'host.docker.internal').replace('127.0.1', 'host.docker.internal').replace('127.0.0.1', 'host.docker.internal')
                
                use_openai_compat = '/v1' in base_url
                api_url = f"{base_url}/chat/completions" if use_openai_compat else f"{base_url}/api/chat"
                
                if use_openai_compat:
                    payload = {
                        "model": self.config.model_name,
                        "messages": messages,
                        "temperature": 0.3,
                        "stream": False
                    }
                else:
                    payload = {
                        "model": self.config.model_name,
                        "messages": messages,
                        "options": {"temperature": 0.3},
                        "stream": False
                    }
                
                resp = requests.post(api_url, json=payload, timeout=60)
                resp.raise_for_status()
                data = resp.json()
                
                if use_openai_compat:
                    return data['choices'][0]['message']['content']
                else:
                    return (data.get('message') or {}).get('content') or ''
                    
            else:
                # OpenAI Compatible
                import openai
                client = openai.OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)
                completion = client.chat.completions.create(
                    model=self.config.model_name,
                    messages=messages,
                    temperature=0.3
                )
                return completion.choices[0].message.content
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def parse_task(self, text, user=None):
        """
        Analyze the user's intent from the text.
        Returns a JSON object with 'intent' and 'content' (and possibly other metadata).
        """
        default_prompt = """
        Analyze the user's intent.
        Available Intents:
        - create_customer: User wants to add/create a new company/customer.
        - create_opportunity: User wants to add/create a sales opportunity/deal.
        - create_todo: User wants to create a todo/task.
        - query_data: User wants to search/query information.
        - other: Any other intent.

        Output JSON:
        {
            "intent": "ONE_OF_ABOVE",
            "content": "The original or cleaned text relevant to the intent",
            "confidence": 0.0-1.0
        }
        """
        prompt = self._get_prompt('task_analysis', default_prompt)
        data = self._call_llm_json(prompt, text, user=user, intent='analyze_task', entity='task')
        
        if not data or 'error' in data:
            # Fallback Logic based on keywords
            import re
            t = text or ''
            intent = 'other'
            if re.search(r'(?:新建|创建|新增|录入)(?:一个|一条)?(?:客户|公司|企业)', t):
                intent = 'create_customer'
            elif re.search(r'(?:新建|创建|新增|录入)(?:一个|一条)?(?:商机|机会|销售机会)', t):
                intent = 'create_opportunity'
            elif re.search(r'(?:新建|创建|新增|录入)(?:一个|一条)?(?:待办|任务)', t):
                intent = 'create_todo'
            elif re.search(r'(?:查询|查找|搜索|找一下)', t):
                intent = 'query_data'
            
            return {'intent': intent, 'content': t, 'confidence': 0.5, 'source': 'fallback'}
            
        return data

    def parse_customer(self, text, user=None):
        default_prompt = """
        Extract Customer Company info.
        Output JSON keys:
        - name: Company Name.
        - industry: Industry.
        - scale: One of [SMALL, MEDIUM, LARGE, ENTERPRISE, GOV].
        - legal_representative: Legal Rep Name.
        - website: URL.
        - region: Region or City (e.g. "Beijing", "Shenyang").
        - address: Full address if available.
        - contact_name: Key contact person name.
        - contact_title: Key contact person title.
        """
        prompt = self._get_prompt(PromptTemplate.Scene.CUSTOMER, default_prompt)
        data = self._call_llm_json(prompt, text, user=user, intent='create', entity='customer')
        if not data or ('error' in data):
            import re
            t = text or ''
            name = None
            # 增强的正则匹配：支持 "客户名称: XX" 或 "新建客户 XX" 或 "创建客户 XX" 或 "创建一个客户 XX"
            m_name = re.search(r'客户名称[:：]\s*([^\s，,。;；]+)', t) or \
                     re.search(r'(?:新建|创建)(?:一个|一项)?客户[，, ]\s*([^\s，,。;；]{2,40})', t) or \
                     re.search(r'客户[，, ]\s*([^\s，,。;；]{2,40})', t)
            
            if m_name: name = m_name.group(1).strip()
            
            ind = None
            m_ind = re.search(r'行业[:：]\s*([^\s，,。;；]+)', t) or re.search(r'([^\s，,。;；]+)行业', t)
            if m_ind: ind = m_ind.group(1).strip()
            
            reg = None
            m_reg = re.search(r'(?:区域|地点)[:：]\s*([^\s，,。;；]+)', t) or \
                    re.search(r'在([^\s，,。;；]{1,10})', t) or \
                    re.search(r'地点\s*([^\s，,。;；]{1,10})', t)
            if m_reg: reg = m_reg.group(1).strip()
            
            fallback = {'name': name, 'industry': ind, 'region': reg, 'status': 'POTENTIAL'}
            if data and 'error' in data: fallback['error'] = data['error']
            return fallback
        return data
        
    def parse_contact(self, text, user=None):
        prompt = """
        Extract Contact Person info.
        Output JSON keys:
        - name: Name.
        - title: Job Title.
        - phone: Phone Number.
        - email: Email.
        - customer_name: Company Name they belong to.
        """
        data = self._call_llm_json(prompt, text, user=user, intent='create', entity='contact')
        return data
