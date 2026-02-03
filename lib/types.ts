export type Annotation = {
  id: string;
  start: number;
  end: number;
  note: string;
};

export type StoredState = {
  text: string;
  annotations: Annotation[];
};
