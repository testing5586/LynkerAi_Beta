export async function FormatterAgent(layer1, layer2, socket) {
  const final = {
    layer1_raw: layer1,
    layer2_standardized: layer2
  };

  return {
    layer: "layer3",
    success: true,
    export_ready: true,
    data: final
  };
}
