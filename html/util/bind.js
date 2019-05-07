// https://glitch.com/edit/#!/fantasy-desk?path=bind.js:20:3
import { directive } from 'https://unpkg.com/lit-html@1.0.0/lit-html.js?module';

const bindMap = new WeakSet();

// 2-way binding helper... use with caution.
export const bind = directive((context, propName, eventName) => (part) => {
  if (!bindMap.has(part)) {
    // add the event listener 1x.
    bindMap.add(part);
    // default event name to Polymer convention for naming notifying events.
    eventName = eventName || 'change';
    part.committer.element.addEventListener(eventName, (ev) => {
      let target = ev.target
      if (target.tagName == 'INPUT') {
        let v;
        switch (target.type) {
          case 'text':
          case 'number':
            v = parseInt(target.value)
            break
          case 'checkbox':
          case 'select':
            v = target.checked
            break
        }
        context[propName] = v;
      }
    });
  }
  part.setValue(context[propName]);
});
