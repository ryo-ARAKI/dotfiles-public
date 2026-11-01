// Fixture, not human adoption: roundtrip-spectrum r2, variant a, 05-resumed.json.
// CeTZ 0.5.3, official Universe checked 2026-10-31; Typst 0.15.1.
#import "@preview/cetz:0.5.3"
#let schematic(unit:0.15mm) = {
  cetz.canvas(length:unit,{
    import cetz.draw: *
    let q(x,y) = (x,480-y)
    let ink = rgb("#203e50")
    // Every cubic control point is explicit, editable, and reflected in Y once.
    let profile-start=(100,300)
    let profile-control-1=(165.123456789,200.987654321)
    let profile-control-2=(200,120)
    let profile-join=(300,140)
    let profile-control-3=(450,170)
    let profile-control-4=(550,250)
    let profile-end=(700,330)
    let transfer-start=(300,310)
    let transfer-control-1=(400,290)
    let transfer-control-2=(500,280.123456789)
    let transfer-end=(600,310)
    let arrowhead(a,b,paint,w) = {
      let dx=b.at(0)-a.at(0);let dy=b.at(1)-a.at(1)
      let length=calc.sqrt(dx*dx+dy*dy);let ux=dx/length;let uy=dy/length
      line(q(b.at(0)+0.7*w*ux,b.at(1)+0.7*w*uy),
        q(b.at(0)-6.3*w*ux - 3.5*w*uy,b.at(1)-6.3*w*uy+3.5*w*ux),
        q(b.at(0)-6.3*w*ux+3.5*w*uy,b.at(1)-6.3*w*uy - 3.5*w*ux),close:true,fill:paint,stroke:none)
    }
    let label(x,y,body,size:24,paint:ink) = {
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
    rect(q(90,350),q(90+295.123456789,90),radius:2,fill:rgb("#eef5fa"),stroke:none)
    merge-path({
      bezier(q(..profile-start),q(..profile-join),q(..profile-control-1),q(..profile-control-2))
      bezier(q(..profile-join),q(..profile-end),q(..profile-control-3),q(..profile-control-4))
    },stroke:(paint:navy,thickness:4*unit,cap:"round",join:"round"))
    line(q(70,370),q(740,370),stroke:(paint:black,thickness:2*unit,cap:"round"))
    arrowhead((70,370),(740,370),black,2)
    line(q(70,370),q(70,60),stroke:(paint:black,thickness:2*unit,cap:"round"))
    arrowhead((70,370),(70,60),black,2)
    bezier(q(..transfer-start),q(..transfer-end),q(..transfer-control-1),q(..transfer-control-2),stroke:(paint:eastern,thickness:3*unit,cap:"round"))
    arrowhead(transfer-control-2,transfer-end,eastern,3)
    label(440.123456789,90,([定性形状],[Profile]),size:26,paint:blue)
    label(720,410,[位置 x])
    label(85,35,[強度])
    label(450,340,([移送],[Transfer]),paint:eastern)
    // Deleted dashed guide stays absent. This is qualitative, not measured data.
  })
}
#set page(width:auto,height:auto,margin:0pt)
#set text(font:("Noto Sans","Noto Sans CJK JP"))
#schematic()
