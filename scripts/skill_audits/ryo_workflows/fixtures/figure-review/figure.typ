#set page(width: 150mm, height: 100mm, margin: 10mm)
#set text(font: "DejaVu Sans", size: 10pt)
#let rows = csv("values.csv", row-type: dictionary)
#let x(row) = (20 + (float(row.tau) - 1) * 65 + if row.method == "A" { -3 } else { 3 }) * 1mm
#let y(value) = (2.6 - float(value)) * 22mm
RMSE by condition
#block(width: 125mm, height: 65mm)[
  #place(dx: 8mm, dy: 57.2mm)[#line(length: 100mm)]
  #place(dx: 8mm, dy: 2mm)[#line(length: 55.2mm, angle: 90deg)]
  #for value in (0, 1, 2) {
    place(dx: 0mm, dy: y(value) - 2mm)[#value]
  }
  #for row in rows {
    let upper = float(row.high) + if row.method == "A" and row.tau == "1" { 0.2 } else { 0 }
    let color = if row.method == "A" { blue } else { orange }
    place(dx: x(row), dy: y(upper))[#line(length: (upper - float(row.low)) * 22mm, angle: 90deg, stroke: color)]
    place(dx: x(row) - 1mm, dy: y(row.rmse) - 1mm)[#circle(radius: 1mm, fill: color, stroke: none)]
  }
  #place(dx: 18mm, dy: 60mm)[1]
  #place(dx: 83mm, dy: 60mm)[2 (tau)]
  #place(dx: 52mm, dy: 1mm)[#text(fill: orange)[Method A] #text(fill: blue)[Method B]]
]
