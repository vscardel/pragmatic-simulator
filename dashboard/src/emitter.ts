class EventEmitter<EventMap extends Record<string, any[]>> extends EventTarget {
  emit(name: string, ...detail: EventMap[keyof EventMap]) {
    this.dispatchEvent(new CustomEvent(name, {detail}));
  }

  on(name: string, callback: (e: CustomEvent) => void) {
    this.addEventListener(name, callback as EventListener);
  }
}
