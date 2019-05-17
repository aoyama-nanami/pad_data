// https://glitch.com/edit/#!/fantasy-desk?path=bind.js:20:3
import {directive, AttributePart, BooleanAttributePart} from 'https://unpkg.com/lit-html@1.0.0/lit-html.js?module';
import {LitElement} from 'https://unpkg.com/lit-element@2.1.0/lit-element.js?module';

const bindMap = new WeakSet();

// 2-way binding helper... use with caution.
export const bind = directive((context, ...props) => (part) => {
  const lastProp = props.pop();
  const element = (part instanceof AttributePart) ?
      part.committer.element : part.element;
  if (!bindMap.has(part)) {
    bindMap.add(part);
    element.addEventListener('change', (ev) => {
      const target = ev.target;
      let v;
      if (target.tagName == 'INPUT') {
        switch (target.type) {
          case 'text':
            v = target.value;
            break;
          case 'number':
            v = parseInt(target.value);
            break;
          case 'checkbox':
          case 'select':
            v = target.checked;
            break;
          case 'radio':
            break;
        }
      } else if (target.tagName == 'SELECT') {
        switch (target.dataset.type) {
          case 'string':
            v = target.value;
            break;
          default:
            v = parseInt(target.value);
        }
      } else if (target instanceof LitElement) {
        if (target.checked !== undefined) {
          v = target.checked
        } else {
          v = target.value;
        }
      }
      let obj = context;
      props.forEach((prop) => obj = obj[prop]);
      obj[lastProp] = v;

      context.requestUpdate();
      context.triggerChange && context.triggerChange()
    });
  }
  let obj = context;
  props.forEach((prop) => obj = obj[prop]);
  obj = obj[lastProp];
  if (obj instanceof Array || obj instanceof Object) {
    part.setValue(JSON.stringify(obj));
  } else {
    part.setValue(obj);
  }
});

export const bindRadio = directive((context, ...props) => (part) => {
  const lastProp = props.pop();
  if (!bindMap.has(part)) {
    bindMap.add(part);
    part.committer.element.addEventListener('change', (ev) => {
      const target = ev.target;
      let v = target.value;
      switch (target.dataset.type) {
        case 'number':
          v = parseInt(v);
          break;
      }
      let obj = context;
      props.forEach((prop) => obj = obj[prop]);
      obj[lastProp] = v;
      context.requestUpdate();
    });
  }
  let obj = context;
  props.forEach((prop) => obj = obj[prop]);
  part.setValue(obj[lastProp] == part.committer.element.value);
});
