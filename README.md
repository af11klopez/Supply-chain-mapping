# Cobalt-to-EV + end-of-life viewer

[Download the HTML viewer](output/Cobalt_to_EV_EOL_conectado.html?raw=true) · [Download all files as ZIP](combined-map.zip?raw=true)

Save the HTML file and open it in a browser. The embedded map works offline. GitHub's file viewer displays the HTML source rather than running the interactive map.

To view the map online with GitHub Pages, open repository **Settings → Pages**, choose **Deploy from a branch**, select **main** and **/ (root)**, then save. The root `index.html` opens the finished viewer.

The original viewer SVG is retained byte for byte: original nodes, colors, positions, and connections remain unchanged. EOL-1 through EOL-10 are stacked below Tier 9 in source order. Two vehicle handoffs connect Tier 9 to the EOL network.

## Connections

The 20 cross-section EOL connections use separate right-hand lanes, marked **P01–P20**. The 13 recovered-material returns use separate left-hand lanes, marked **R01–R13**, with green dashed arrows. Each arrow ends on its destination node. Routes avoid node rectangles and do not share collinear segments. Perpendicular line crossings can remain; white underlays distinguish them.

Select a connection, then use **Origin** or **Destination** to jump to either endpoint. The selected connection is highlighted while others fade; **Show all** restores the full map. Hover over a connection for its description.

Recovered cobalt and nickel sulfate feed the NMC/NCA pCAM inputs; MHP returns to refining; recycled NMC pCAM feeds NMC CAM manufacture; regenerated NMC/NCA CAM, graphite, and copper/aluminium foil feed cell manufacture. Qualified recovered LiOH feeds NMC/NCA CAM manufacture. Destination-specific purity, chemistry, and performance requirements still apply. Repaired batteries/modules retain their source endpoint because the supplied map does not define their specific vehicle or pack acceptance route.

## Rebuild

Requires Node.js, Python 3, and Chromium at `/usr/bin/chromium`. Run `npm ci`, then `npm run build`. Run `npm run check` for route geometry and browser interaction checks.

Edit `sources/eol.mmd` to update EOL operations. `sources/original-viewer.html` retains the fixed original layout. `combined-supply-chain.mmd` is the editable semantic map, including return connections; rendering that complete source independently can rearrange nodes. The HTML build renders only EOL sections and overlays routed connections without rearranging the original SVG.
