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
    // Contract: undirected magnification across three scales; the dashed
    // enclosure is model scope, not a time axis or a transport arrow.
    content((48, 50), [階層と適用範囲 / Scale hierarchy])
    rect((3, 16), (25, 40), name: "micro", fill: pale, stroke: teal)
    for x in (8, 14, 20) {
      for y in (22, 28, 34) { circle((x, y), radius: 1, fill: teal, stroke: none) }
    }
    rect((32, 16), (57, 40), name: "meso", fill: none, stroke: ink)
    // Native closed-path clipping rather than white paint over the swirls.
    clip(rect((33, 17), (56, 39)), {
      for y in (17, 25, 33) {
        bezier((29, y), (61, y+3), (40, y+13), (49, y - 8), stroke: teal)
      }
    })
    rect((65, 16), (93, 40), name: "macro", fill: pale, stroke: teal)
    line((68, 22), (90, 22), stroke: (paint: ink, thickness: 1pt))
    line((68, 28), (90, 28), stroke: (paint: ink, thickness: 1pt))
    line((68, 34), (90, 34), stroke: (paint: ink, thickness: 1pt))
    // Border anchors follow box dimensions. No arrowheads: correspondence.
    line("micro.east", "meso.west", stroke: ink)
    line("meso.east", "macro.west", stroke: ink)
    content((14, 11), [Microscale])
    content((44.5, 11), [Mesoscale])
    content((79, 11), [Macroscale])
    rect((30, 7), (95, 43), fill: none,
      stroke: (paint: ink, dash: "dashed", thickness: 0.5pt))
    content((62.5, 3), [破線内：モデル範囲 / model scope])
  })
}

#set page(width: auto, height: auto, margin: 3mm)
#set text(font: ("Noto Sans", "Noto Sans CJK JP"), size: 9pt)
#schematic()
