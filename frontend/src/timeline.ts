export interface TimelineOptions {
  minYear: number;
  maxYear: number;
  initialYear?: number;
  onChange: (year: number) => void;
}

interface DynastyMark {
  year: number;
  label: string;
}

const DYNASTY_MARKS: DynastyMark[] = [
  { year: -221, label: '秦' },
  { year: 202, label: '汉' },
  { year: 618, label: '唐' },
  { year: 960, label: '宋' },
  { year: 1271, label: '元' },
  { year: 1368, label: '明' },
  { year: 1644, label: '清' },
];

const SPEEDS = [
  { label: '1x', ms: 800 },
  { label: '2x', ms: 400 },
  { label: '5x', ms: 160 },
];

export class TimelineControl {
  private minYear: number;
  private maxYear: number;
  private currentYear: number;
  private onChange: (year: number) => void;
  private playing = false;
  private speedIdx = 0;
  private rafId: number | null = null;
  private lastTick = 0;
  private debounceTimer: number | null = null;

  private container: HTMLElement;
  private slider: HTMLInputElement;
  private yearLabel: HTMLElement;
  private playBtn: HTMLElement;
  private speedBtns: HTMLElement[] = [];

  constructor(options: TimelineOptions) {
    this.minYear = options.minYear;
    this.maxYear = options.maxYear;
    this.currentYear = options.initialYear ?? options.maxYear;
    this.onChange = options.onChange;

    this.container = document.createElement('div');
    this.container.className = 'timeline-bar';

    // Play button
    this.playBtn = document.createElement('button');
    this.playBtn.className = 'timeline-play-btn';
    this.playBtn.textContent = '▶';
    this.playBtn.title = '播放 / 暂停';
    this.playBtn.addEventListener('click', () => this.toggle());
    this.container.appendChild(this.playBtn);

    // Slider wrap
    const sliderWrap = document.createElement('div');
    sliderWrap.className = 'timeline-slider-wrap';

    this.slider = document.createElement('input');
    this.slider.type = 'range';
    this.slider.className = 'timeline-slider';
    this.slider.min = String(this.minYear);
    this.slider.max = String(this.maxYear);
    this.slider.value = String(this.currentYear);
    this.slider.step = '1';
    this.slider.addEventListener('input', () => {
      this.currentYear = parseInt(this.slider.value, 10);
      this.yearLabel.textContent = this.formatYear(this.currentYear);
      if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
      this.debounceTimer = window.setTimeout(() => {
        this.debounceTimer = null;
        this.onChange(this.currentYear);
      }, 150);
    });
    sliderWrap.appendChild(this.slider);

    // Dynasty marks
    const marks = document.createElement('div');
    marks.className = 'timeline-marks';
    DYNASTY_MARKS.forEach((dm) => {
      const span = document.createElement('span');
      span.className = 'timeline-mark';
      span.textContent = dm.label;
      span.title = dm.label + ' ' + String(dm.year);
      span.addEventListener('click', () => this.setYear(dm.year));
      marks.appendChild(span);
    });
    sliderWrap.appendChild(marks);

    this.container.appendChild(sliderWrap);

    // Year label
    this.yearLabel = document.createElement('span');
    this.yearLabel.className = 'timeline-year-label';
    this.yearLabel.textContent = this.formatYear(this.currentYear);
    this.container.appendChild(this.yearLabel);

    // Speed buttons
    const speedWrap = document.createElement('div');
    speedWrap.className = 'timeline-speed-wrap';
    SPEEDS.forEach((s, i) => {
      const btn = document.createElement('button');
      btn.className = 'timeline-speed-btn';
      if (i === 0) btn.classList.add('active');
      btn.textContent = s.label;
      btn.addEventListener('click', () => {
        this.speedIdx = i;
        this.speedBtns.forEach((b, j) => b.classList.toggle('active', j === i));
        if (this.playing) {
          this.stopAnimation();
          this.lastTick = 0;
          this.startAnimation();
        }
      });
      speedWrap.appendChild(btn);
      this.speedBtns.push(btn);
    });
    this.container.appendChild(speedWrap);
  }

  getElement(): HTMLElement {
    return this.container;
  }

  getYear(): number {
    return this.currentYear;
  }

  setYear(year: number): void {
    const clamped = Math.max(this.minYear, Math.min(this.maxYear, year));
    if (clamped === this.currentYear) return;
    this.currentYear = clamped;
    this.slider.value = String(clamped);
    this.yearLabel.textContent = this.formatYear(clamped);
    this.onChange(clamped);
  }

  play(): void {
    if (this.playing) return;
    this.playing = true;
    this.playBtn.textContent = '⏸';
    this.lastTick = 0;
    this.startAnimation();
  }

  pause(): void {
    if (!this.playing) return;
    this.playing = false;
    this.playBtn.textContent = '▶';
    this.stopAnimation();
  }

  toggle(): void {
    if (this.playing) {
      this.pause();
    } else {
      this.play();
    }
  }

  isPlaying(): boolean {
    return this.playing;
  }

  destroy(): void {
    this.playing = false;
    if (this.debounceTimer !== null) {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = null;
    }
    this.stopAnimation();
    this.container.remove();
  }

  private startAnimation(): void {
    const tick = (ts: number) => {
      if (!this.playing) return;
      if (this.lastTick === 0) this.lastTick = ts;
      const elapsed = ts - this.lastTick;
      const interval = SPEEDS[this.speedIdx].ms;
      if (elapsed >= interval) {
        this.lastTick = ts - (elapsed % interval);
        const next = this.currentYear + 1;
        if (next > this.maxYear) {
          this.pause();
          return;
        }
        this.setYear(next);
      }
      this.rafId = requestAnimationFrame(tick);
    };
    this.rafId = requestAnimationFrame(tick);
  }

  private stopAnimation(): void {
    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }

  private formatYear(year: number): string {
    if (year < 0) {
      return '前' + String(-year) + '年';
    }
    return '公元' + String(year) + '年';
  }
}
