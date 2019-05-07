import { LitElement, html, css } from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module'

export function iconCheckbox(iconClass, checked, disabled) {
  return html`
    <label class="icon-checkbox">
      <input type="checkbox"
             .checked="${checked}"
             .disabled="${disabled}">
      <div class="${iconClass}"></div>
    </label>
  `
}

export function toggleCheckbox(text, checked, disabled) {
  return html`
    <label class="toggle-checkbox">
      <input type="checkbox"
             .checked="${checked}"
             .disabled="${disabled}">
      <span class="material-icons"></span>
      ${text}
    </label>
  `
}
