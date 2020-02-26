import {html} from '../util/external_lib.js';
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

export function radio(text, name, value, checked) {
  return html`
    <label class="radio pointer">
      <input type="radio"
             class="radio"
             name="${name}"
             value="${value}"
             .checked="${checked}">
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
