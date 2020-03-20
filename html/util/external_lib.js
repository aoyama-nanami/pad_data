import {LitElement, html, css} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';
import {directive, AttributePart} from 'https://unpkg.com/lit-html@^1.0.0/lit-html.js?module';

console.assert(new Set(litElementVersions).size == 1, litElementVersions);
console.assert(new Set(litHtmlVersions).size == 1, litHtmlVersions);

export {LitElement, html, css};
export {directive, AttributePart};
