using Godot;
using System;
using System.Text.Json;
namespace Ngumach.VisualReboot;
public partial class VisualPreview
{
    /// <summary>Native atlas review; frozen pose samples, not an FPS demonstration.</summary>
    private async void RunMotionArtReview()
    {
        try
        {
            if(_capture==null)throw new InvalidOperationException("Motion review requires --capture absolute.png");
            _hudHidden=true;var layer=new CanvasLayer{Layer=200};AddChild(layer);
            using var doc=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/motion16/manifest.json"));
            var folder=System.IO.Path.GetDirectoryName(_capture)!;
            foreach(var action in new[]{"idle","walk","attack","cast"})
            {
                foreach(var old in layer.GetChildren()){layer.RemoveChild(old);old.QueueFree();}
                layer.AddChild(new ColorRect{Position=Vector2.Zero,Size=new Vector2(1280,720),Color=new Color(.09f,.11f,.19f)});
                var title=new Label{Text="MINH KIẾM · "+action.ToUpperInvariant()+" · 16 KHUNG × 8 HƯỚNG",Position=new Vector2(26,12)};title.AddThemeFontSizeOverride("font_size",21);layer.AddChild(title);
                for(int f=0;f<16;f++){var l=new Label{Text=f.ToString("00"),Position=new Vector2(65+f*72,40)};l.AddThemeFontSizeOverride("font_size",11);layer.AddChild(l);}
                for(int d=0;d<8;d++)
                {
                    var clip=doc.RootElement.GetProperty("clips").GetProperty(action)[d];float scale=54/clip.GetProperty("sourceHeight").GetSingle();
                    var label=new Label{Text=new[]{"N","NE","E","SE","S","SW","W","NW"}[d],Position=new Vector2(15,91+d*75)};label.AddThemeFontSizeOverride("font_size",13);layer.AddChild(label);
                    for(int f=0;f<16;f++)
                    {
                        var frame=clip.GetProperty("frames")[f];var r=frame.GetProperty("rect");var p=frame.GetProperty("pivot");bool flip=frame.GetProperty("flip").GetBoolean();
                        var rect=new Rect2(r[0].GetSingle(),r[1].GetSingle(),r[2].GetSingle(),r[3].GetSingle());var pivot=new Vector2(p[0].GetSingle(),p[1].GetSingle());if(flip)pivot.X=rect.Size.X-pivot.X;
                        layer.AddChild(new Sprite2D{Texture=GD.Load<Texture2D>("res://assets/motion16/"+frame.GetProperty("file").GetString()),RegionEnabled=true,RegionRect=rect,Centered=false,Offset=-pivot,FlipH=flip,Scale=Vector2.One*scale,Position=new Vector2(80+f*72,125+d*75),TextureFilter=TextureFilterEnum.Nearest});
                    }
                }
                var footer=new Label{Text="Ảnh kiểm tư thế tĩnh · không phải phép đo FPS · các hướng đối xứng có metadata lật ảnh",Position=new Vector2(26,680)};footer.AddThemeFontSizeOverride("font_size",13);layer.AddChild(footer);
                for(int i=0;i<4;i++)await ToSignal(GetTree(),SceneTree.SignalName.PhysicsFrame);
                await ToSignal(RenderingServer.Singleton,RenderingServer.SignalName.FramePostDraw);
                var path=System.IO.Path.Combine(folder,"motion16_"+action+".png");var error=GetViewport().GetTexture().GetImage().SavePng(path);if(error!=Error.Ok)throw new InvalidOperationException("Motion review capture: "+error);
            }
            GD.Print("MOTION_ART_REVIEW PASS actions=4 directions=8 poses=16");GetTree().Quit();
        }
        catch(Exception ex){GD.PushError("MOTION_ART_REVIEW FAIL "+ex);GetTree().Quit(1);}
    }
}
