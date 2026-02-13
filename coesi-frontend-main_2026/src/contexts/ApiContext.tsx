import React, { createContext, useContext, useMemo, ReactNode } from 'react';
import { CIM_WIZARD_BASE, CIM_WIZARD_URLS } from '../config/apiConfig';

type EndpointSpec = string | ((...args: any[]) => string);

export interface ApiDescriptor {
  baseUrl: string;
  endpoints: Record<string, EndpointSpec>;
}

const defaultDescriptor: ApiDescriptor = {
  baseUrl: CIM_WIZARD_BASE,
  endpoints: { ...CIM_WIZARD_URLS },
};

const ApiContext = createContext<ApiDescriptor>(defaultDescriptor);

export const ApiProvider = ({
  descriptor,
  children,
}: {
  descriptor?: Partial<ApiDescriptor>;
  children: ReactNode;
}) => {
  const value = useMemo<ApiDescriptor>(
    () => ({
      baseUrl: descriptor?.baseUrl || defaultDescriptor.baseUrl,
      endpoints: { ...defaultDescriptor.endpoints, ...(descriptor?.endpoints || {}) },
    }),
    [descriptor]
  );

  return <ApiContext.Provider value={value}>{children}</ApiContext.Provider>;
};

export const useApiDescriptor = () => useContext(ApiContext);

