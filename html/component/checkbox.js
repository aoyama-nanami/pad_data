import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';

export function toggleCheckbox(text, checked, disabled, onchange) {
  return html`
    <label class="toggle-checkbox">
      <input type="checkbox"
             .checked="${checked}"
             .disabled="${disabled}"
             @change="${onchange}">
      <span class="material-icons"></span>
      ${text}
    </label>
  `;
}

export function radio(text, name, value, checked, disabled) {
  return html`
    <label class="radio">
      <input type="radio"
             name="${name}"
             value="${value}"
             .checked="${checked}"
             .disabled="${disabled}"
             @change="${onchange}">
      <span class="material-icons"></span>
      ${text}
    </label>
  `;
}
