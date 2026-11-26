import { loadFont as loadSans } from "@remotion/google-fonts/InstrumentSans";
import { loadFont as loadMono } from "@remotion/google-fonts/GeistMono";
import { loadFont as loadWord } from "@remotion/google-fonts/Jost";

// Example palette for a fictional app: a light surface, deep blue, warm orange for emphasis.
export const paper = "#F5F8FC";
export const sheet = "#FFFFFF";
export const ink = "#0B2545";
export const muted = "#51647F";
export const rule = "#D6E0EC";
export const blue = "#1F4E9C";
export const blueLight = "#8DB3E8";
export const orange = "#F28C28";
export const good = "#1E8A5A";
export const warn = "#B86E00";
export const bad = "#C2410C";

const sans = loadSans("normal", { weights: ["400", "500", "600", "700"], subsets: ["latin"] });
const mono = loadMono("normal", { weights: ["400", "500", "600"], subsets: ["latin"] });
const word = loadWord("normal", { weights: ["500"], subsets: ["latin"] });

export const fontSans = `${sans.fontFamily}, Helvetica, Arial, sans-serif`;
export const fontMono = `${mono.fontFamily}, Menlo, monospace`;
export const fontWord = `${word.fontFamily}, Futura, sans-serif`;
