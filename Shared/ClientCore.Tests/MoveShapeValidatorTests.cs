using NguMach.Client.Core.Encounter;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class MoveShapeValidatorTests
    {
        [Fact]
        public void Cone_Valid()
        {
            var s = new MoveShape { KindRaw = "CONE", RangeWu = 5, FacingX = 1, FacingY = 0, AngleDegrees = 60 };
            Assert.True(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Cone_ZeroFacing_Invalid()
        {
            var s = new MoveShape { KindRaw = "CONE", RangeWu = 5, FacingX = 0, FacingY = 0, AngleDegrees = 60 };
            Assert.False(MoveShapeValidator.IsValid(s, out var r));
            Assert.False(string.IsNullOrEmpty(r));
        }

        [Fact]
        public void Cone_MissingFacing_Invalid()
        {
            var s = new MoveShape { KindRaw = "CONE", RangeWu = 5, AngleDegrees = 60 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Cone_BadAngle_Invalid()
        {
            var s = new MoveShape { KindRaw = "CONE", RangeWu = 5, FacingX = 1, FacingY = 0, AngleDegrees = 0 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Cone_NonFinite_Invalid()
        {
            var s = new MoveShape { KindRaw = "CONE", RangeWu = 5, FacingX = double.NaN, FacingY = 0, AngleDegrees = 60 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Cone_UnknownKind_Invalid()
        {
            var s = new MoveShape { KindRaw = "TRIANGLE", RangeWu = 5, FacingX = 1, FacingY = 0 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Circle_Valid()
        {
            var s = new MoveShape { KindRaw = "CIRCLE", RadiusWu = 3 };
            Assert.True(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Circle_ZeroRadius_Invalid()
        {
            var s = new MoveShape { KindRaw = "CIRCLE", RadiusWu = 0 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Circle_CarryingFacing_Invalid()
        {
            var s = new MoveShape { KindRaw = "CIRCLE", RadiusWu = 3, FacingX = 1, FacingY = 0 };
            Assert.False(MoveShapeValidator.IsValid(s, out var r));
            Assert.Contains("facing", r);
        }

        [Fact]
        public void Circle_CarryingConeFields_Invalid()
        {
            var s = new MoveShape { KindRaw = "CIRCLE", RadiusWu = 3, AngleDegrees = 90, RangeWu = 4 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Annulus_Valid()
        {
            var s = new MoveShape { KindRaw = "ANNULUS", InnerRadiusWu = 1, OuterRadiusWu = 4 };
            Assert.True(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Annulus_InnerNotLessOuter_Invalid()
        {
            var s = new MoveShape { KindRaw = "ANNULUS", InnerRadiusWu = 4, OuterRadiusWu = 4 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Annulus_CarryingFacing_Invalid()
        {
            var s = new MoveShape { KindRaw = "ANNULUS", InnerRadiusWu = 1, OuterRadiusWu = 4, FacingX = 1, FacingY = 0 };
            Assert.False(MoveShapeValidator.IsValid(s, out var r));
            Assert.Contains("facing", r);
        }

        [Fact]
        public void Null_Invalid()
        {
            Assert.False(MoveShapeValidator.IsValid(null, out _));
        }
    }
}
