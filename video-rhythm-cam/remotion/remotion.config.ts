import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);

// 设置使用 Puppeteer 浏览器
Config.setChromiumOpenGlRenderer("angle");

export { Config };
