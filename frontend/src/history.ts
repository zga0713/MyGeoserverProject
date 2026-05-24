import type Feature from 'ol/Feature';
import type Geometry from 'ol/geom/Geometry';
import type VectorSource from 'ol/source/Vector';

export interface Command {
  type: 'insert' | 'update' | 'delete';
  feature: Feature;
  execute(): void;
  undo(): void;
}

export class InsertCommand implements Command {
  type: 'insert' = 'insert';
  feature: Feature;
  source: VectorSource;

  constructor(feature: Feature, source: VectorSource) {
    this.feature = feature;
    this.source = source;
  }

  execute(): void {
    this.source.addFeature(this.feature);
  }

  undo(): void {
    this.source.removeFeature(this.feature);
  }
}

export class UpdateCommand implements Command {
  type: 'update' = 'update';
  feature: Feature;
  oldGeom: Geometry;
  oldProps: Record<string, unknown>;
  newGeom: Geometry;
  newProps: Record<string, unknown>;

  constructor(
    feature: Feature,
    oldGeom: Geometry,
    oldProps: Record<string, unknown>,
    newGeom: Geometry,
    newProps: Record<string, unknown>,
  ) {
    this.feature = feature;
    this.oldGeom = oldGeom;
    this.oldProps = oldProps;
    this.newGeom = newGeom;
    this.newProps = newProps;
  }

  execute(): void {
    this.feature.setGeometry(this.newGeom);
    const { geometry, ...props } = this.newProps as Record<string, unknown> & { geometry?: unknown };
    this.feature.setProperties(props);
  }

  undo(): void {
    this.feature.setGeometry(this.oldGeom);
    const { geometry, ...props } = this.oldProps as Record<string, unknown> & { geometry?: unknown };
    this.feature.setProperties(props);
  }
}

export class DeleteCommand implements Command {
  type: 'delete' = 'delete';
  feature: Feature;
  source: VectorSource;

  constructor(feature: Feature, source: VectorSource) {
    this.feature = feature;
    this.source = source;
  }

  execute(): void {
    this.source.removeFeature(this.feature);
  }

  undo(): void {
    this.source.addFeature(this.feature);
  }
}

export class CommandHistory {
  private undoStack: Command[] = [];
  private redoStack: Command[] = [];
  onChange: (() => void) | null = null;

  execute(cmd: Command): void {
    cmd.execute();
    this.undoStack.push(cmd);
    this.redoStack = [];
    if (this.onChange) this.onChange();
  }

  record(cmd: Command): void {
    this.undoStack.push(cmd);
    this.redoStack = [];
    if (this.onChange) this.onChange();
  }

  undo(): void {
    if (this.undoStack.length === 0) return;
    const cmd = this.undoStack.pop()!;
    cmd.undo();
    this.redoStack.push(cmd);
    if (this.onChange) this.onChange();
  }

  redo(): void {
    if (this.redoStack.length === 0) return;
    const cmd = this.redoStack.pop()!;
    cmd.execute();
    this.undoStack.push(cmd);
    if (this.onChange) this.onChange();
  }

  clear(): void {
    this.undoStack = [];
    this.redoStack = [];
    if (this.onChange) this.onChange();
  }

  get length(): number {
    return this.undoStack.length;
  }
}
