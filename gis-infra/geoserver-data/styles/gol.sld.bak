<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0"
    xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd"
    xmlns="http://www.opengis.net/sld"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <!-- a named layer is the basic building block of an sld document -->

  <NamedLayer>
    <Name>Default Polygon</Name>
    <UserStyle>
        <!-- they have names, titles and abstracts -->

      <Title>Grey Polygon</Title>
      <Abstract>A sample style that just prints out a grey interior with a black outline</Abstract>
      <!-- FeatureTypeStyles describe how to render different features -->
      <!-- a feature type for polygons -->

      <FeatureTypeStyle>
        <!--FeatureTypeName>Feature</FeatureTypeName-->
        <Rule>
          <Name>Rule 1</Name>
          <Title>Gray Polygon with Black Outline</Title>
          <Abstract>A polygon with a gray fill and a 1 pixel black outline</Abstract>

          <!-- like a linesymbolizer but with a fill too -->
          <PolygonSymbolizer>

            <Geometry><ogc:PropertyName>geometry</ogc:PropertyName></Geometry>

            <Fill>
              <CssParameter name="fill">#AAAAAA</CssParameter>
              <CssParameter name="fill-opacity">1.0</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#000000</CssParameter>
              <CssParameter name="stroke-width">1</CssParameter>
              <CssParameter name="storke-opacity">1.0</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        <Rule>
          <MaxScaleDenominator>32000</MaxScaleDenominator>

          <TextSymbolizer>
            <Label>
              <ogc:PropertyName>name_ch</ogc:PropertyName>
            </Label>

            <Font>
              <CssParameter name="font-family">Microsoft YaHei</CssParameter>
              <CssParameter name="font-weight">Bold</CssParameter>
              <CssParameter name="font-size">14</CssParameter>
            </Font>

            <LabelPlacement>
              <PointPlacement>
                <AnchorPoint>
                  <AnchorPointX>0.5</AnchorPointX>
                  <AnchorPointY>0.5</AnchorPointY>
                </AnchorPoint>
                <Displacement>
                  <DisplacementX>0</DisplacementX>
                  <DisplacementY>-15</DisplacementY>
                </Displacement>
              </PointPlacement>
            </LabelPlacement>

            <Halo>
              <Radius>
                <ogc:Literal>2</ogc:Literal>
              </Radius>
              <Fill>
                <CssParameter name="fill">#FFFFFF</CssParameter>
              </Fill>
            </Halo>

            <Fill>
              <CssParameter name="fill">#000000</CssParameter>
            </Fill>
          </TextSymbolizer>
        </Rule>

        </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>