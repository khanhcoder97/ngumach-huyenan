using NguMach.Client.Core.Encounter;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class MoveShapeValidatorTests
    {
        [Fact]
        public void Cone_Valid()
        {
            var s = new MoveShape { Type = "cone", AngleDegrees = 60, Range = 5, FacingX = 1, FacingY = 0 };
            Assert.True(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Cone_ZeroFacing_Invalid()
        {
            var s = new MoveShape { Type = "cone", AngleDegrees = 60, Range = 5, FacingX = 0, FacingY = 0 };
            Assert.False(MoveShapeValidator.IsValid(s, out var r));
            Assert.False(string.IsNullOrEmpty(r));
        }

        [Fact]
        public void Cone_BadAngle_Invalid()
        {
            var s = new MoveShape { Type = "cone", AngleDegrees = 0, Range = 5, FacingX = 1, FacingY = 0 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Cone_NonFinite_Invalid()
        {
            var s = new MoveShape { Type = "cone", AngleDegrees = 60, Range = 5, FacingX = double.NaN, FacingY = 0 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Circle_Valid()
        {
            var s = new MoveShape { Type = "circle", Radius = 3 };
            Assert.True(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Circle_ZeroRadius_Invalid()
        {
            var s = new MoveShape { Type = "circle", Radius = 0 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Annulus_Valid()
        {
            var s = new MoveShape { Type = "annulus", InnerRadius = 1, OuterRadius = 4 };
            Assert.True(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Annulus_InnerNotLessOuter_Invalid()
        {
            var s = new MoveShape { Type = "annulus", InnerRadius = 4, OuterRadius = 4 };
            Assert.False(MoveShapeValidator.IsValid(s, out _));
        }

        [Fact]
        public void Null_Invalid()
        {
            Assert.False(MoveShapeValidator.IsValid(null, out _));
        }
    }
}
