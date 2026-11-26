import { TransitionSeries, linearTiming, springTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import type { ShotMeta, ZoomKey } from "../../kit/shot-meta";
import { AppWindow, NumberCallout, Spotlight } from "../../kit/film/AppWindow";
import { EndCard, TitleCard } from "../../kit/film/Cards";
import { ChapterTag, FilmCaption, Stage, SyntheticChip } from "../../kit/film/pieces";
import { Sound, type Cue, type Duck } from "../../kit/film/Sound";
import type { FilmTheme } from "../../kit/film/theme";
import { Film, filmFrames } from "../../kit/film/Film";
import { MAIN, SOCIAL } from "./filmCuts";
import boardMeta from "../../../public/footage/northwind-tasks/board.json";
import { bad, blue, blueLight, fontMono, fontSans, fontWord, ink, muted, orange, paper, rule } from "./theme";

const FOOT = "footage/northwind-tasks";
const BD = boardMeta as unknown as ShotMeta;

// Colors and type for the fictional app: deep blue and warm orange on a light surface.
export const northwindFilm: FilmTheme = {
  product: "Tasks",
  stage: "#E8EEF6",
  paper,
  ink,
  muted,
  rule,
  accent: orange,
  accentInk: ink,
  ring: [blue, blueLight, orange],
  flag: bad,
  fontSans,
  fontWord,
  fontMono,
};

// The app window on a 16:9 stage: 86% of the 1600x900 capture, centred, captions in the margin below.
const RECT_WIDE = { left: 272, top: 124, width: 1376, height: 774 };
const z = (frame: number, cx: number, cy: number, scale: number): ZoomKey => ({ frame, cx, cy, scale });

// ------------------------------------------------------------------ look test: title, one scene, one callout, end
const LOOK = { title: 108, scene: 342, end: 126, t1: 18, t2: 18 };
export const LOOK_TOTAL = LOOK.title + LOOK.scene + LOOK.end - LOOK.t1 - LOOK.t2; // 540 = 18 s = 30 beats
const SCENE_AT = LOOK.title - LOOK.t1; // 90, on beat 5
const END_AT = SCENE_AT + LOOK.scene - LOOK.t2; // 414, on beat 23

// Source frames of board.mp4 (real time, rate 1).
const boardZoom = [z(0, 800, 450, 1), z(60, 800, 450, 1), z(95, 760, 300, 1.3), z(190, 760, 320, 1.3), z(225, 800, 480, 1.15), z(320, 800, 480, 1.15)];
const CALLOUT = { from: 98, to: 192 };
const CAPS = [
  { from: 6, to: 94, text: "Forty-two open tasks, in three columns." },
  { from: 100, to: 196, text: "Seven are overdue. They stand out at a glance.", highlight: ["overdue"] },
];

const BoardScene: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <Stage theme={northwindFilm}>
      <AppWindow theme={northwindFilm} src={`${FOOT}/board.mp4`} meta={BD} trimBefore={0} rate={1} zoom={boardZoom} rect={RECT_WIDE} label="Northwind Tasks  ·  Board"
        overlay={(geo) => (
          <>
            <Spotlight geo={geo} mark={BD.marks.overdue} from={CALLOUT.from} to={CALLOUT.to} theme={northwindFilm} />
            <NumberCallout geo={geo} mark={BD.marks.overdue} from={CALLOUT.from} to={CALLOUT.to} theme={northwindFilm}
              label="Overdue this week" value="7" note="of 42 open tasks" source="From the captured app · sample data" cardWidth={440} />
          </>
        )} />
      <div style={{ position: "absolute", left: RECT_WIDE.left, top: 40 }}><ChapterTag theme={northwindFilm} index="01" label="The board" delay={10} /></div>
      <div style={{ position: "absolute", right: RECT_WIDE.left, top: 30 }}><SyntheticChip theme={northwindFilm} size={20} delay={16} /></div>
      {CAPS.map((c, i) => (
        <Sequence key={i} name={`Caption ${i + 1}`} from={c.from} durationInFrames={c.to - c.from} premountFor={fps}>
          <FilmCaption theme={northwindFilm} text={c.text} duration={c.to - c.from} highlight={c.highlight} />
        </Sequence>
      ))}
    </Stage>
  );
};

const lookDucks: Duck[] = [
  ...CAPS.map((c) => ({ from: SCENE_AT + c.from, to: SCENE_AT + c.to })),
  { from: SCENE_AT + CALLOUT.from, to: SCENE_AT + CALLOUT.to },
];
const lookCues: Cue[] = [
  { at: 4, sfx: "tick" },
  { at: 14, sfx: "hit", volume: 0.2 },
  { at: SCENE_AT - 8, sfx: "whoosh" },
  { at: SCENE_AT + 217, sfx: "tick" }, // recorded click: open a card
  { at: SCENE_AT + CALLOUT.from, sfx: "hit" },
  { at: SCENE_AT + CALLOUT.from + 18, sfx: "chime" },
  { at: END_AT - 10, sfx: "whoosh" },
  { at: END_AT + 6, sfx: "hit", volume: 0.22 },
];

export const NorthwindLook: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <TransitionSeries>
        <TransitionSeries.Sequence name="Title" durationInFrames={LOOK.title} premountFor={fps}>
          <TitleCard theme={northwindFilm} layout="wide" headline="One board for everything your team is working on." highlight={["board"]} sub="Running on a fictional team of eight people." />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: LOOK.t1 })} />
        <TransitionSeries.Sequence name="Board" durationInFrames={LOOK.scene} premountFor={fps}>
          <BoardScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({ direction: "from-bottom" })} timing={springTiming({ config: { damping: 200 }, durationInFrames: LOOK.t2 })} />
        <TransitionSeries.Sequence name="End" durationInFrames={LOOK.end} premountFor={fps}>
          <EndCard theme={northwindFilm} layout="wide" line1="Real screens." line2="Sample data." />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <Sound bed="audio/northwind-look-bed.wav" ducks={lookDucks} cues={lookCues} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ the films (main 16:9, social 9:16 and 16:9)
export const NorthwindFilmMain: React.FC = () => <Film cut={MAIN} theme={northwindFilm} layout="wide" />;
export const NorthwindFilmSocialTall: React.FC = () => <Film cut={SOCIAL} theme={northwindFilm} layout="tall" />;
export const NorthwindFilmSocialWide: React.FC = () => <Film cut={SOCIAL} theme={northwindFilm} layout="wide" />;
export const FILM_MAIN_TOTAL = filmFrames(MAIN);
export const FILM_SOCIAL_TOTAL = filmFrames(SOCIAL);
