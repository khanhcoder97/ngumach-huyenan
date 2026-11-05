using Server.Health.World;
namespace Server.Health.Smoke;
public static class AuthoredTerrainSelfCheck
{
    public static int Run(string path)
    {
        int checks=0;void Check(bool ok,string name){checks++;if(!ok)throw new InvalidOperationException(name);}
        try
        {
            var t=new AuthoredTerrain(path);
            foreach(var r in t.Solids)Check(!t.Walkable(r.X+r.W/2,r.Y+r.H/2,.6),"solid center blocked: "+r.Id);
            for(int x=18;x<=64;x++)Check(t.Walkable(x,0,.6),"first quest street clear: "+x);
            Check(t.Walk(18,0,64,0,.6).Status==LineOfSightStatus.Allowed,"whole quest street is traversable");
            Check(t.Walk(37,-5.8,37,-10.5,.6).Status==LineOfSightStatus.Allowed,"connected dock deck is walkable");
            Check(!t.Walkable(39,-10,.6),"water outside dock is blocked");
            Check(!t.Walkable(37,-12,.6),"foot cannot overhang dock end into water");
            Check(t.Walk(39,-5,39,-11,.6).IsBlocked,"swept move cannot tunnel across water");
            Check(t.Walk(27,0,27,5,.6).IsBlocked,"swept move cannot tunnel through hall");
            Check(t.Walk(27,0,27,5,0).IsBlocked,"zero radius still respects solid interiors");
            Check(t.Walk(double.NaN,0,1,0,.6).IsBlocked,"nonfinite move rejected");
            Check(t.Walk(18,0,19,0,-1).IsBlocked,"invalid radius rejected");
            Console.WriteLine("AUTHORED_TERRAIN_SELF_CHECK PASS assertions="+checks);return 0;
        }
        catch(Exception ex){Console.Error.WriteLine("AUTHORED_TERRAIN_SELF_CHECK FAIL "+ex);return 1;}
    }
}
