import type { ShotMeta, ZoomKey } from "../../kit/shot-meta";
import type { FilmClip, FilmCut } from "../../kit/film/timeline";
import boardMeta from "../../../public/footage/northwind-tasks/board.json";
import taskMeta from "../../../public/footage/northwind-tasks/task.json";
import weeklyMeta from "../../../public/footage/northwind-tasks/weekly.json";

// Example films for a fictional team task app. Plain data: scenes, camera keys (footage px,
// source frames), captions (scene frames) and callouts on exact on-screen values.
// Read by Film.tsx and scripts/film-plan.mjs.
const BD = boardMeta as unknown as ShotMeta;
const TK = taskMeta as unknown as ShotMeta;
const WK = weeklyMeta as unknown as ShotMeta;
const z = (frame: number, cx: number, cy: number, scale: number): ZoomKey => ({ frame, cx, cy, scale });
const FOOT = "footage/northwind-tasks";

// Tall windows show about 850 footage px across: stay on the left of the content column
// or on the figure being called out.
const clips: Record<string, FilmClip> = {
  board: { src: `${FOOT}/board.mp4`, meta: BD,
    wide: [z(0, 800, 450, 1), z(60, 800, 450, 1), z(95, 760, 300, 1.3), z(190, 760, 320, 1.3), z(225, 800, 480, 1.15), z(320, 800, 480, 1.15)],
    tall: [z(0, 600, 420, 1), z(90, 600, 330, 1.1), z(200, 640, 470, 1.05), z(320, 640, 470, 1.05)] },
  task: { src: `${FOOT}/task.mp4`, meta: TK,
    wide: [z(0, 800, 450, 1), z(22, 800, 450, 1), z(70, 800, 330, 1.32), z(112, 860, 470, 1.22), z(196, 860, 470, 1.22), z(232, 800, 560, 1.12), z(342, 800, 560, 1.12), z(400, 800, 450, 1)],
    tall: [z(0, 640, 400, 1), z(80, 760, 430, 1.05), z(200, 760, 430, 1.05), z(240, 640, 560, 1), z(400, 640, 560, 1)] },
  weekly: { src: `${FOOT}/weekly.mp4`, meta: WK,
    wide: [z(0, 800, 450, 1), z(60, 800, 330, 1.25), z(150, 800, 380, 1.3), z(220, 800, 450, 1.05), z(300, 800, 450, 1)],
    tall: [z(0, 640, 400, 1), z(80, 790, 430, 1.05), z(220, 640, 520, 1), z(300, 640, 520, 1)] },
};

const SYN = "From the captured app · sample data";

const overdue = { clip: "board", mark: BD.marks.overdue, from: 98, to: 192,
  callout: { label: "Overdue this week", value: "7", note: "of 42 open tasks", source: SYN, cardWidth: 440 } };
const done = { clip: "weekly", mark: WK.marks.done, from: 95, to: 190,
  callout: { label: "Done this week", value: "35", note: "up from 28 last week", source: SYN, cardWidth: 460 } };

export const MAIN: FilmCut = {
  id: "Northwind-Film-Main-16x9", bed: "audio/northwind-main-bed.wav", key: "D", clips,
  scenes: [
    { kind: "title", name: "Title", beats: 6, headline: "One board for everything your team is working on.", highlight: ["board"], sub: "Running on a fictional team of eight people." },
    { kind: "shot", name: "Board", chapter: "The board", window: "Northwind Tasks  ·  Board",
      segs: [{ clip: "board", from: 0, to: 320 }],
      focus: [overdue, { clip: "board", mark: BD.marks.card, from: 204, to: 258 }],
      caps: [
        { from: 6, to: 94, text: "Forty-two open tasks, in three columns." },
        { from: 100, to: 196, text: "Seven are overdue. They stand out at a glance.", highlight: ["overdue"] },
        { from: 204, to: 312, text: "Open a card to see the detail." },
      ] },
    { kind: "shot", name: "Task detail", chapter: "One task", window: "Northwind Tasks  ·  Task detail",
      segs: [{ clip: "task", from: 0, to: 400 }],
      focus: [{ clip: "task", mark: TK.marks.assignee, from: 118, to: 200 }],
      caps: [
        { from: 8, to: 112, text: "Each task has an owner, a due date and a short checklist.", highlight: ["owner"] },
        { from: 208, to: 330, text: "Comments and files stay with the task." },
        { from: 336, to: 392, text: "Next: the weekly summary." },
      ] },
    { kind: "shot", name: "Weekly summary", chapter: "The week", window: "Northwind Tasks  ·  Weekly summary  ·  Sample data",
      segs: [{ clip: "weekly", from: 0, to: 300, rate: 1.15 }],
      focus: [done],
      caps: [
        { from: 4, to: 80, text: "Sample data: a fictional team with made-up tasks.", highlight: ["Sample", "data"] },
        { from: 100, to: 200, text: "Thirty-five tasks done this week, seven more than last." },
        { from: 206, to: 260, text: "Share the summary with one click." },
      ] },
    { kind: "end", name: "End", beats: 7 },
  ],
};

export const SOCIAL: FilmCut = {
  id: "Northwind-Film-Social", bed: "audio/northwind-social-bed.wav", key: "D", clips,
  scenes: [
    { kind: "title", name: "Hook", beats: 4, headline: "What is overdue this week?", highlight: ["overdue"], sub: "One board shows it." },
    { kind: "shot", name: "Board", chapter: "The board", window: "Tasks  ·  Board",
      segs: [{ clip: "board", from: 60, to: 270, rate: 1.3 }],
      focus: [{ ...overdue, from: 92, to: 200 }],
      caps: [{ from: 4, to: 150, text: "Forty-two open tasks. Seven overdue." }] },
    { kind: "shot", name: "Task", chapter: "One task", window: "Tasks  ·  Task detail",
      segs: [{ clip: "task", from: 30, to: 280, rate: 1.4 }],
      focus: [{ clip: "task", mark: TK.marks.assignee, from: 80, to: 190 }],
      caps: [{ from: 4, to: 60, text: "Every task has an owner.", highlight: ["owner."] }, { from: 140, to: 176, text: "Comments stay with it." }] },
    { kind: "shot", name: "Weekly", chapter: "The week", window: "Tasks  ·  Weekly summary  ·  Sample data",
      segs: [{ clip: "weekly", from: 30, to: 300, rate: 1.5 }],
      focus: [{ ...done, from: 60, to: 160 }],
      caps: [{ from: 4, to: 40, text: "Sample data.", highlight: ["Sample"] }, { from: 116, to: 176, text: "Thirty-five tasks done." }] },
    { kind: "end", name: "End", beats: 4 },
  ],
};
