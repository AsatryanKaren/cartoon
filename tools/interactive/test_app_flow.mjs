// Click through a story in headless Chromium (the app's dev server must run on :5173).
// usage: node tools/interactive/test_app_flow.mjs "<story title on its card>"
// Needs playwright-core (npm i playwright-core in a scratch folder) and Chromium at /opt/pw-browsers/chromium.
// That Chromium cannot play H.264: test with a VP9 copy of the story (ffmpeg -c:v libvpx-vp9 -c:a libopus,
// same .mp4 names, in a temporary app/public/stories/_test folder + a temporary index.json entry). Remove after.
// Keys: n = skip clip / time out, 1/2 = answer choice 1/2, h = show what was heard.
import { chromium } from "playwright-core";
const b = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium",
  args: ["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream", "--autoplay-policy=no-user-gesture-required"] });
const p = await b.newPage({ viewport: { width: 960, height: 540 } });
const log = [];
p.on("console", m => { if (m.type() === "error") log.push("console: " + m.text()); });
p.on("pageerror", e => log.push("pageerror: " + e.message));
const front = async () => p.evaluate(() => {
  const v = document.querySelector("video.front"); if (!v) return null;
  return { src: v.dataset.x, t: +v.currentTime.toFixed(1), listening: document.querySelector(".listening")?.textContent || "" };
});
await p.goto("http://localhost:5173/");
await p.waitForTimeout(800);
await p.screenshot({ path: "test_picker.png" });
await p.getByText(process.argv[2] || "HYTEST").click();
await p.waitForTimeout(1500);
await p.locator("button.start").click();
const step = async (label, ms) => { await p.waitForTimeout(ms); console.log(label, JSON.stringify(await front())); };
await step("intro playing", 1000);
await p.keyboard.press("n");
await step("listening", 1200);
await p.screenshot({ path: "test_listening.png" });
await p.keyboard.press("2");
await step("tree", 800);
await p.keyboard.press("n"); await step("middle", 800);
await p.keyboard.press("n"); await step("q2 listening", 1000);
await p.keyboard.press("1"); await step("boat", 800);
await p.keyboard.press("n"); await step("ending", 800);
await p.keyboard.press("n"); await step("end screen", 800);
await p.screenshot({ path: "test_end.png" });
console.log((await p.textContent("body")).slice(0, 200));
console.log(log.join("\n") || "no errors");
await b.close();
