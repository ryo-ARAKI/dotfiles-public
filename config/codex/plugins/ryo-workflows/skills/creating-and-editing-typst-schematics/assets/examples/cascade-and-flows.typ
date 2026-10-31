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
    // Contract: the gray profile is qualitative, solid teal arrows are
    // rightward transport, dashed orange arrow is leftward feedback.
    // Neither profile height nor spacing encodes measured values.
    content((48, 50), [定性的な流れ / Qualitative flows])
    line((7, 13), (90, 13), stroke: ink)
    bezier((9, 37), (87, 20), (29, 43), (59, 18), stroke: (paint: gray, thickness: 1.2pt))
    content((23, 42), [$E(k)$：模式曲線])
    for (a,b) in (((15, 28), (39, 28)), ((45, 23), (69, 23))) {
      line(a, b, stroke: (paint: teal, thickness: 1.2pt), mark: (end: ">"))
    }
    content((50, 33), [Transport / 輸送])
    bezier((78, 8), (22, 8), (65, 1), (35, 1),
      stroke: (paint: rgb("#a44e21"), dash: "dashed", thickness: 1pt), mark: (end: ">"))
    content((50, 9), [Feedback / 帰還])
    content((49, 17), [scale →])
    content((48, 47), [線高・距離は実測値ではない])
  })
}

#set page(width: auto, height: auto, margin: 3mm)
#set text(font: ("Noto Sans", "Noto Sans CJK JP"), size: 9pt)
#schematic()
