import {html} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {icon} from '../common.js';

export function toggleCheckbox(text, checked, disabled, onchange) {
  return html`
    <label class="toggle-checkbox pointer">
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
    <label class="radio pointer">
      <input type="radio"
             name="${name}"
             value="${value}"
             .checked="${checked}"
             .disabled="${disabled}">
      <span class="material-icons"></span>
      ${text}
    </label>
  `;
}

export function iconRadio(iconName, name, value, checked, type) {
  return html`
    <label class="icon-radio">
      <input type="radio"
             name="${name}"
             value="${value}"
             .checked="${checked}"
             data-type="${type}">
      ${icon(iconName)}
    </label>
  `;
}
