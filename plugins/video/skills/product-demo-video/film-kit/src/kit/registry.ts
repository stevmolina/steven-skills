import type { ComponentType } from "react";

export type CompositionDef = {
  id: string; // e.g. "Northwind-Main-16x9"
  component: ComponentType;
  durationInFrames: number;
  width: number;
  height: number;
  fps?: number;
};
