import { useEffect } from "react";

function webAppVersionMajor(version?: string): number {
  if (!version) {
    return 0;
  }
  const major = Number.parseInt(version.split(".")[0] ?? "0", 10);
  return Number.isNaN(major) ? 0 : major;
}

const FULLSCREEN_TOP_BUFFER = 6;

function computeAppSafeTop(
  device?: TelegramSafeAreaInset,
  content?: TelegramSafeAreaInset,
  isFullscreen?: boolean,
): number {
  const deviceTop = device?.top ?? 0;
  const contentTop = content?.top ?? 0;

  if (!isFullscreen) {
    return Math.max(deviceTop, contentTop);
  }

  const base = Math.max(deviceTop, contentTop);
  if (base === 0) {
    return 52 + FULLSCREEN_TOP_BUFFER;
  }

  const gap = Math.min(deviceTop, contentTop);
  if (gap === 0) {
    return base + 10 + FULLSCREEN_TOP_BUFFER;
  }

  if (Math.abs(deviceTop - contentTop) <= 6) {
    return base + FULLSCREEN_TOP_BUFFER;
  }

  return Math.round(base + gap * 0.35) + FULLSCREEN_TOP_BUFFER;
}

function applySafeAreaInsets(webApp: TelegramWebApp) {
  const root = document.documentElement;
  const device = webApp.safeAreaInset;
  const content = webApp.contentSafeAreaInset;
  const isFullscreen = Boolean(webApp.isFullscreen);

  const setInset = (prefix: "safe-area" | "content-safe-area", inset?: TelegramSafeAreaInset) => {
    if (!inset) {
      return;
    }
    root.style.setProperty(`--tg-${prefix}-inset-top`, `${inset.top}px`);
    root.style.setProperty(`--tg-${prefix}-inset-bottom`, `${inset.bottom}px`);
    root.style.setProperty(`--tg-${prefix}-inset-left`, `${inset.left}px`);
    root.style.setProperty(`--tg-${prefix}-inset-right`, `${inset.right}px`);
  };

  setInset("safe-area", device);
  setInset("content-safe-area", content);

  root.style.setProperty("--app-safe-top", `${computeAppSafeTop(device, content, isFullscreen)}px`);

  root.classList.toggle("tg-fullscreen", isFullscreen);
}

export function useTelegram() {
  const webApp = window.Telegram?.WebApp;

  useEffect(() => {
    if (!webApp) {
      return;
    }

    const syncSafeArea = () => applySafeAreaInsets(webApp);

    webApp.ready();
    webApp.expand();
    syncSafeArea();

    if (webAppVersionMajor(webApp.version) >= 8 && typeof webApp.requestFullscreen === "function") {
      webApp.requestFullscreen();
      window.setTimeout(syncSafeArea, 0);
      window.setTimeout(syncSafeArea, 150);
      window.setTimeout(syncSafeArea, 400);
    }

    webApp.setHeaderColor?.("secondary_bg_color");
    webApp.setBackgroundColor?.("bg_color");

    webApp.onEvent?.("safeAreaChanged", syncSafeArea);
    webApp.onEvent?.("contentSafeAreaChanged", syncSafeArea);
    webApp.onEvent?.("fullscreenChanged", syncSafeArea);

    return () => {
      webApp.offEvent?.("safeAreaChanged", syncSafeArea);
      webApp.offEvent?.("contentSafeAreaChanged", syncSafeArea);
      webApp.offEvent?.("fullscreenChanged", syncSafeArea);
      document.documentElement.classList.remove("tg-fullscreen");
    };
  }, [webApp]);

  return {
    webApp,
    user: webApp?.initDataUnsafe?.user,
    colorScheme: webApp?.colorScheme ?? "light",
  };
}
