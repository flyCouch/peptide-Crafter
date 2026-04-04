/* Project: Peptide Mark I - Single Hex Pair (V147)
   __FILE__: hex_pair.scad
   __DATE__: 2026-04-04
   __TIME__: 19:45
*/

// --- Project Header Print ---
echo("PROJECT: Peptide Mark I - Hex Pair V147");
echo("COMPILE DATE:", "2026-04-04");
echo("COMPILE TIME:", "19:45");

// Parameters directly from combineTunksHexPairs3.py
pair_w   = 40.0;
pair_d   = 55.0;
pair_h   = 100.0;
chamfer  = 15.0;

// Machining Dimensions
barrel_d = 18.0;   // The narrow fluid chamber
fluid_h  = 85.0;   // Hole depth (leaves 15mm solid bottom)
septa_d  = 20.5;   // The shoulder/pocket diameter
pocket_h = 10.0;   // Depth of the shoulder from the TOP
clip_d   = 24.0;   // The C-clip groove diameter
clip_h   = 1.5;    // Thickness of the groove
meat_top = 5.0;    // Material remaining above the clip

$fn = 100;

module hex_outer_shell() {
    linear_extrude(height = pair_h)
    polygon(points=[
        [chamfer, 0], [pair_w - chamfer, 0], [pair_w, chamfer],
        [pair_w, pair_d - chamfer], [pair_w - chamfer, pair_d],
        [chamfer, pair_d], [0, pair_d - chamfer], [0, chamfer]
    ]);
}

module v147_internal_cuts() {
    union() {
        // 1. THE BARREL: 18mm diameter, 85mm deep from the top.
        // It starts at Z=15 and goes to the top (Z=100).
        translate([0, 0, pair_h - fluid_h])
            cylinder(d = barrel_d, h = fluid_h + 1);
        
        // 2. THE SHOULDER (Septa Pocket): 20.5mm diameter.
        // It cuts 10mm deep from the top face.
        translate([0, 0, pair_h - pocket_h])
            cylinder(d = septa_d, h = pocket_h + 1);
            
        // 3. THE C-CLIP GROOVE: 24.0mm diameter.
        // Sits 5mm below the top.
        translate([0, 0, pair_h - meat_top - clip_h])
            cylinder(d = clip_d, h = clip_h);
    }
}

module final_assembly() {
    difference() {
        hex_outer_shell();
        
        // Positioning the two barrels at Y=13.75 and Y=41.25 per your Python script
        translate([pair_w/2, 13.75, 0]) v147_internal_cuts();
        translate([pair_w/2, 41.25, 0]) v147_internal_cuts();
    }
}

final_assembly();
