/**
 * RunningHub ComfyUI Extension — Custom widgets and UI enhancements.
 *
 * This file is loaded by ComfyUI's frontend when the RunningHub
 * custom node package is installed. Add custom widget implementations
 * here as needed.
 */

import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ComfyUI.RunningHub",

    async setup() {
        console.log("[RunningHub] Extension loaded");
    },
});
