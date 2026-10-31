// Direct dependency: CeTZ 0.5.3; stable release checked 2026-10-31.
// https://typst.app/universe/package/cetz/
// Typst >=0.15.0. No research files, custom templates, or data are needed.
#import "@preview/cetz:0.5.3"

// Export only this body when embedding. Page/font defaults below are confined
// to standalone module content; local label sizing does not change host text.
#let schematic(unit: 0.8mm, label-size: 7pt) = {
  set text(size: label-size)
  set par(leading: 0.35em)
  cetz.canvas(length: unit, {
    import cetz.draw: *
    let ink = rgb("#244e66")
    let teal = rgb("#267b79")
    let pale = rgb("#e0f0ef")
    rect((0, 0), (96, 54), fill: white, stroke: none)
    // Contract: candidates -> selection -> update; update -> candidates is
    // repetition, update -> stop is a conditional exit. Distances are qualitative.
    // Tidy example from the HTML horizontal fixture: 960x540 draft -> 96x54.
    // Group (50.3,60.2,700.4,310.6) -> (5,6,70,31) in tidy units.
    // Derive a shared row, common size, and 22-unit pitch rather than rounding
    // three positions independently. CeTZ y = 54 - draft-y / 10.
    let gx = 5
    let gy = 6
    let w = 18
    let h = 9
    let row-top = gy + 9
    let cy = 54 - row-top - h/2
    rect((gx, 54 - gy - 31), (gx+70, 54 - gy), fill: rgb("#f2f7fa"),
      stroke: (paint: ink, dash: "dashed", thickness: 0.5pt), radius: 1)
    content((40, 45.5), [探索 / Search])
    for (i, label) in ([候補 α\ Candidates], [選択\ Select], [更新\ Update]).enumerate() {
      let x = gx + 3 + i*22
      rect((x, 54 - row-top - h), (x+w, 54 - row-top), name: "stage-"+str(i+1),
        fill: pale, stroke: teal, radius: 0.7)
      content((x+w/2, cy), align(center, label))
    }
    rect((79, 30), (88.5, 39), name: "stop", fill: pale, stroke: teal, radius: 0.7)
    content("stop.center", align(center)[終了\ Stop])
    line("stage-1.east", (28, cy), (29, cy), "stage-2.west", stroke: ink, mark: (end: ">"))
    line("stage-2.east", "stage-3.west", stroke: ink, mark: (end: ">"))
    line("stage-3.east", "stop.west", stroke: ink, mark: (end: ">"))
    line("stage-3.south", (61, 14), (17, 14), "stage-1.south", stroke: ink, mark: (end: ">"))
    content((28, 25.9), align(center)[選択へ\ select])
    content((77, 43), [停止条件])
    content((40, 11), [反復 / repeat])
  })
}

#set page(width: auto, height: auto, margin: 3mm)
#set text(font: ("Noto Sans", "Noto Sans CJK JP"), size: 9pt)
#schematic()
