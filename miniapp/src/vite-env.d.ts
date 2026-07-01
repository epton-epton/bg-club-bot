/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

interface TelegramSafeAreaInset {
  top: number;
  bottom: number;
  left: number;
  right: number;
}

interface TelegramWebApp {
  ready: () => void;
  expand: () => void;
  requestFullscreen?: () => void;
  exitFullscreen?: () => void;
  isFullscreen?: boolean;
  version?: string;
  safeAreaInset?: TelegramSafeAreaInset;
  contentSafeAreaInset?: TelegramSafeAreaInset;
  onEvent?: (eventType: string, eventHandler: () => void) => void;
  offEvent?: (eventType: string, eventHandler: () => void) => void;
  setHeaderColor?: (color: string) => void;
  setBackgroundColor?: (color: string) => void;
  colorScheme: "light" | "dark";
  themeParams: Record<string, string | undefined>;
  initDataUnsafe?: {
    user?: {
      id: number;
      first_name?: string;
      last_name?: string;
      username?: string;
      language_code?: string;
    };
  };
  initData?: string;
  platform?: string;
}

interface TelegramNamespace {
  WebApp: TelegramWebApp;
}

interface Window {
  Telegram?: TelegramNamespace;
}
