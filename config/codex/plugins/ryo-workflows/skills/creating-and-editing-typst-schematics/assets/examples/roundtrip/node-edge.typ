// Fixture, not human adoption: roundtrip-node-edge r2, variant a, 05-resumed.json.
// CeTZ 0.5.3 checked against official Universe on 2026-10-31; Typst 0.15.1.
// Ordinary compilation needs this source and cached CeTZ/oxifmt only, no JSON/app.
#import "@preview/cetz:0.5.3"
#let schematic(unit: 0.15mm) = {
  cetz.canvas(length: unit, {
    import cetz.draw: *
    let q(x,y) = (x,480-y)
    let ink = rgb("#192d40")
    let outline = rgb("#267b79")
    let pale = rgb("#e0f0ef")
    let group-x = 42.123456789
    let group-y = 63.987654321
    let row = group-y + 100
    let input-x = group-x + 41.02564102566154
    let select-x = group-x + 276.9230769232154
    let refine-x = group-x + 470
    let original-width = 153.84615384623078
    // Local helpers preserve host typography and the draft's filled arrowhead.
    let relation(a,b,paint) = {
      line(q(..a),q(..b),stroke:(paint:paint,thickness:2.5*unit))
      let dx=b.at(0)-a.at(0); let dy=b.at(1)-a.at(1)
      let length=calc.sqrt(dx*dx+dy*dy); let ux=dx/length;let uy=dy/length
      let w=2.5
      line(q(b.at(0)+0.7*w*ux,b.at(1)+0.7*w*uy),
        q(b.at(0)-6.3*w*ux - 3.5*w*uy,b.at(1)-6.3*w*uy+3.5*w*ux),
        q(b.at(0)-6.3*w*ux+3.5*w*uy,b.at(1)-6.3*w*uy - 3.5*w*ux),close:true,fill:paint,stroke:none)
    }
    let label(x,y,body,size:26,paint:ink) = {
      let lines=if type(body)==array {body} else {(body,)}
      for (i,line) in lines.enumerate() {
        // Same 1.2-font-size line-center spacing as the shared SVG renderer.
        content(q(x,y - (lines.len()-1)*size*0.6 + i*size*1.2),{
          set text(size:size*unit,fill:paint)
          align(center,line)
        })
      }
    }
    rect(q(0,480),q(800,0),fill:white,stroke:none)
    rect(q(group-x,group-y+300),q(group-x+666.666666667,group-y),radius:12,
      fill:rgb("#f2f7fa"),stroke:(paint:rgb("#8cabb9"),thickness:2*unit,dash:(8*unit,5*unit)))
    // Background -> relations -> nodes -> labels, as in Schemock.
    relation((input-x+original-width,row+40),(select-x,row+40),rgb("#23566b"))
    relation((select-x+original-width,row+40),(refine-x,row+40),eastern)
    rect(q(input-x,row+80),q(input-x+original-width,row),radius:7,fill:pale,stroke:(paint:outline,thickness:2*unit))
    rect(q(select-x,row+80),q(select-x+original-width,row),radius:7,fill:pale,stroke:(paint:outline,thickness:2*unit))
    rect(q(refine-x,row+80),q(refine-x+150,row),radius:7,fill:pale,stroke:(paint:outline,thickness:2*unit))
    label(input-x+90.123456789,row+40,([候補 α],[Input]),paint:green)
    label(select-x+76.92307692311539,row+40,([選択],[Select]))
    label(410.123456789,390.987654321,[処理の方向],size:24)
    label(refine-x+75,row+40,([精査済],[Refine]))
    // Deleted unused node/label and its incident relation stay absent.
  })
}
#set page(width:auto,height:auto,margin:0pt)
#set text(font:("Noto Sans","Noto Sans CJK JP"))
#schematic()
