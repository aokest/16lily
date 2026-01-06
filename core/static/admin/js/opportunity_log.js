// Toggle action input visibility based on select
function toggleActionFields(sel) {
  var val = sel.value;
  var input = document.querySelector('.action-input');
  if (!input) return;
  if (val && val !== '其他') {
    input.value = val;
    input.parentElement.style.display = 'none';
  } else {
    input.parentElement.style.display = '';
    input.value = '';
  }
}
document.addEventListener('DOMContentLoaded', function() {
  var sel = document.querySelector('.action-select');
  if (sel) toggleActionFields(sel);
});
