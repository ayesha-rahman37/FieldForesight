export const CONFIG = {
  CHAT_STREAMING: (import.meta.env.VITE_CHAT_STREAMING ?? 'true') !== 'false',
  // Defaults to false based on Step 5 latency measurement (REST is ~1ms faster and simpler for single-result responses)
  SCENARIO_STREAMING: (import.meta.env.VITE_SCENARIO_STREAMING ?? 'false') === 'true',
};
