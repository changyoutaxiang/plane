"use client";

import { observer } from "mobx-react";
import { MessageSquare, Info } from "lucide-react";

type TIntercomConfig = {
  isTelemetryEnabled: boolean;
};

export const IntercomConfig: React.FC<TIntercomConfig> = observer((props) => {
  const { isTelemetryEnabled } = props;

  return (
    <>
      <div className="flex items-center gap-14 px-4 py-3 border border-custom-border-200 rounded">
        <div className="grow flex items-center gap-4">
          <div className="shrink-0">
            <div className="flex items-center justify-center w-10 h-10 bg-custom-background-80 rounded-full">
              <MessageSquare className="w-6 h-6 text-custom-text-300/80 p-0.5" />
            </div>
          </div>

          <div className="grow">
            <div className="text-sm font-medium text-custom-text-100 leading-5">Chat with us (Intercom)</div>
            <div className="text-xs font-normal text-custom-text-300 leading-5">
              Intercom 功能已在代码层面全局禁用，此设置不再生效。
            </div>
            <div className="mt-2 flex items-center gap-2 text-xs text-custom-text-400">
              <Info className="w-4 h-4" />
              <span>To re-enable, modify intercom-provider.tsx</span>
            </div>
          </div>

          <div className="ml-auto">
            <div className="px-3 py-1 text-xs font-medium rounded bg-custom-background-90 text-custom-text-400">
              已禁用 (全局)
            </div>
          </div>
        </div>
      </div>
    </>
  );
});
