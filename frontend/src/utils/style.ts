import Feature from 'ol/Feature';
import type { FeatureLike } from 'ol/Feature';
import Style from 'ol/style/Style';
import type { StyleFunction } from 'ol/style/Style';
import Stroke from 'ol/style/Stroke';
import Fill from 'ol/style/Fill';
import Text from 'ol/style/Text';
import CircleStyle from 'ol/style/Circle';

const LABEL_RESOLUTION_THRESHOLD = 0.0004;

export const featureStyleFunction: StyleFunction = (
  featureLike: FeatureLike,
  resolution: number,
): Style | void => {
  if (!(featureLike instanceof Feature)) {
    return;
  }

  const geomType = featureLike.getGeometry()?.getType();

  const styleOpts: {
    stroke: Stroke;
    fill?: Fill;
    image?: CircleStyle;
    text?: Text;
  } = {
    stroke: new Stroke({
      color: 'rgba(0, 0, 0, 1)',
      width: 1,
    }),
  };

  if (resolution < LABEL_RESOLUTION_THRESHOLD) {
    styleOpts.text = createTextStyle(featureLike);
  }

  if (geomType === 'Point') {
    styleOpts.image = new CircleStyle({
      radius: 6,
      fill: new Fill({ color: 'rgba(22, 119, 255, 0.8)' }),
      stroke: new Stroke({ color: 'rgba(255, 255, 255, 1)', width: 2 }),
    });
  } else if (geomType === 'LineString') {
    // stroke only, no fill
  } else {
    styleOpts.fill = new Fill({
      color: 'rgba(170, 170, 170, 1)',
    });
  }

  return new Style(styleOpts);
};

function createTextStyle(feature: Feature): Text {
  return new Text({
    font: 'bold 14px "Microsoft YaHei"',
    text: getText(feature),
    fill: new Fill({
      color: 'rgba(0, 0, 0, 1)',
    }),
    stroke: new Stroke({
      color: 'rgba(255, 255, 255, 1)',
      width: 2,
    }),
    offsetY: -15,
  });
}

function getText(feature: Feature): string {
  const nameCh = feature.get('name_ch');
  if (nameCh != null) {
    return String(nameCh);
  }
  return '';
}
