"use client";

import type { FC } from "react";
import React from "react";

export type IntercomProviderProps = {
  children: React.ReactNode;
};

const IntercomProvider: FC<IntercomProviderProps> = (props) => {
  const { children } = props;

  // Intercom 已禁用 - 直接返回 children，不初始化任何 Intercom 功能
  return <>{children}</>;
};

export default IntercomProvider;
