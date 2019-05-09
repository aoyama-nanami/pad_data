// https://glitch.com/edit/#!/fantasy-desk?path=bind.js:20:3
import {directive} from 'https://unpkg.com/lit-html@1.0.0/lit-html.js?module';

const bindMap = new WeakSet();

// 2-way binding helper... use with caution.
export const bind = directive((context, ...props) => (part) => {
  const lastProp = props.pop();
  if (!bindMap.has(part)) {
    // add the event listener 1x.
    bindMap.add(part);
    part.committer.element.addEventListener('change', (ev) => {
      if (props[0] == 'passiveResistIndexes')
        console.log(context.passiveResistIndexes)

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
        }
      } else if (target.tagName == 'SELECT') {
        switch (target.dataset.type) {
          case 'string':
            v = target.value;
            break;
          default:
            v = parseInt(target.value);
        }
      }
      let obj = context;
      props.forEach((prop) => obj = obj[prop]);
      obj[lastProp] = v;
      context.requestUpdate();
    });
  }
  let obj = context;
  props.forEach((prop) => obj = obj[prop]);
  part.setValue(obj[lastProp]);
});

export const bindRadio = directive((context, ...props) => (part) => {
  const lastProp = props.pop();
  let obj = context;
  props.forEach((prop) => obj = obj[prop]);
  if (!bindMap.has(part)) {
    // add the event listener 1x.
    bindMap.add(part);
    part.committer.element.addEventListener('change', (ev) => {
      const target = ev.target;
      const v = target.value;
      obj[lastProp] = v;
      context.requestUpdate();
    });
  }
  part.setValue(obj[lastProp] == part.committer.element.value);
});
