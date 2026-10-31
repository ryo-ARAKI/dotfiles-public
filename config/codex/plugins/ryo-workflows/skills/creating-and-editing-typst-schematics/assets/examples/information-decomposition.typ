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
    // Contract: two overlapping sets have exclusive A/B regions and a
    // shared region. The stack names those same parts, with schematic heights.
    content((48, 50), [集合と成分 / Decomposition])
    circle((25, 29), radius: 15, fill: rgb("#cce9e5"), stroke: teal)
    circle((42, 29), radius: 15, fill: rgb("#dce6f4").transparentize(25%), stroke: ink)
    content((19, 30), [A only])
    content((34, 29), [Shared])
    content((49, 30), [B only])
    content((25, 10), [$A$])
    content((44, 10), [$B$])
    // A correspondence, not a directed physical flow.
    line((58, 29), (66, 29), stroke: ink)
    rect((68, 17), (93, 25), fill: rgb("#cce9e5"), stroke: ink)
    rect((68, 25), (93, 33), fill: rgb("#b4cdd5"), stroke: ink)
    rect((68, 33), (93, 41), fill: rgb("#dce6f4"), stroke: ink)
    content((80.5, 21), [A only])
    content((80.5, 29), [Shared])
    content((80.5, 37), [B only])
    content((48, 3), [面積・棒高は模式的 / not to scale])
  })
}

#set page(width: auto, height: auto, margin: 3mm)
#set text(font: ("Noto Sans", "Noto Sans CJK JP"), size: 9pt)
#schematic()
