export const socket = {
  emit: (event, data) => console.log("emit", event, data),
  on: (event, cb) => console.log("listen", event),
};
