// https://glitch.com/edit/#!/fantasy-desk?path=bind.js:20:3
import { directive } from 'https://unpkg.com/lit-html@1.0.0/lit-html.js?module';

const bindMap = new WeakSet();

// 2-way binding helper... use with caution.
export const bind = directive((context, ...props) => (part) => {
  let lastProp = props.pop()
  let obj = context;
  props.forEach(prop => obj = obj[prop]);
  if (!bindMap.has(part)) {
    // add the event listener 1x.
    bindMap.add(part);
    part.committer.element.addEventListener('change', (ev) => {
      let target = ev.target
      if (target.tagName == 'INPUT') {
        let v;
        switch (target.type) {
          case 'text':
            v = target.value
            break
          case 'number':
            v = parseInt(target.value)
            break
          case 'checkbox':
          case 'select':
            v = target.checked
            break
        }
        obj[lastProp] = v;
        context.requestUpdate()
      } else if (target.tagName == 'SELECT') {
        obj[lastProp] = parseInt(target.value);
        context.requestUpdate()
      }
    });
  }
  part.setValue(obj[lastProp]);
});

export const bindRadio = directive((context, ...props) => (part) => {
  let lastProp = props.pop()
  let obj = context;
  props.forEach(prop => obj = obj[prop]);
  if (!bindMap.has(part)) {
    // add the event listener 1x.
    bindMap.add(part);
    part.committer.element.addEventListener('change', (ev) => {
      let target = ev.target
      let v = target.value;
      obj[lastProp] = v;
      context.requestUpdate()
    });
  }
  part.setValue(obj[lastProp] == part.committer.element.value);
});
