import $ from 'jquery';
import Map from 'ol/Map';
import View from 'ol/View';
import Projection from 'ol/proj/Projection';
import { get as getProjection, addProjection } from 'ol/proj';
import TileLayer from 'ol/layer/Tile';
import ImageLayer from 'ol/layer/Image';
import VectorLayer from 'ol/layer/Vector';
import XYZ from 'ol/source/XYZ';
import ImageWMS from 'ol/source/ImageWMS';
import VectorSource from 'ol/source/Vector';
import Draw from 'ol/interaction/Draw';
import Select from 'ol/interaction/Select';
import Modify from 'ol/interaction/Modify';
import Snap from 'ol/interaction/Snap';
import WKT from 'ol/format/WKT';
import GeoJSON from 'ol/format/GeoJSON';
import type Geometry from 'ol/geom/Geometry';
import type Feature from 'ol/Feature';
import { featureStyleFunction } from './utils/style.js';
import { InsertCommand, UpdateCommand, DeleteCommand, CommandHistory } from './history.js';
import { sendWFSTransaction } from './utils/wfst.js';

const baseurl = 'http://localhost:8084/';

// Custom EPSG:4326 with axisOrientation 'enu' for GeoServer WFS-T compatibility
const proj4326 = getProjection('EPSG:4326');
const proj = new Projection({
  code: 'EPSG:4326',
  axisOrientation: 'enu',
  units: proj4326!.getUnits(),
  extent: proj4326!.getExtent(),
  global: true,
  worldExtent: proj4326!.getWorldExtent(),
});
addProjection(proj);

// Map and View
const view = new View({
  center: [116.400146, 40.250184],
  zoom: 9,
  projection: 'EPSG:4326',
});

const layers = [
  new TileLayer({
    source: new XYZ({
      url: 'http://rt{0-3}.map.gtimg.com/realtimerender?z={z}&x={x}&y={-y}&type=vector&style=0',
    }),
  }),
  new ImageLayer({
    source: new ImageWMS({
      ratio: 1,
      url: 'http://localhost:8084/geoserver/wms?',
      params: {
        'SERVICE': 'WMS',
        'VERSION': '1.1.0',
        'REQUEST': 'GetMap',
        'FORMAT': 'image/png',
        'TRANSPARENT': true,
        'tiled': true,
        'LAYERS': 'mapgis:v6_time_pref_pgn_utf_wgs84_geoserver',
        'exceptions': 'application/vnd.ogc.se_inimage',
        'singleTile': true,
      },
    }),
  }),
];

const map = new Map({
  target: 'map',
  layers: layers,
  view: view,
});

// Vector layer for editing
const source = new VectorSource({ wrapX: false });
const vector = new VectorLayer({
  source: source,
  style: featureStyleFunction,
});
map.addLayer(vector);

// Command history for undo/redo
const history = new CommandHistory();

// Interactions
let draw: Draw | null = null;
let snap: Snap | null = null;
let modifySnapshot: {
  geometry: Geometry;
  properties: Record<string, unknown>;
} | null = null;

const select = new Select();
const modify = new Modify({
  features: select.getFeatures(),
});

// Snapshot geometry + properties before modify starts
modify.on('modifystart', function (e) {
  const feature = e.features.getArray()[0];
  if (!feature) return;
  const geom = feature.getGeometry();
  if (!geom) return;
  modifySnapshot = {
    geometry: geom.clone() as Geometry,
    properties: { ...feature.getProperties() },
  };
});

// Create UpdateCommand if geometry or properties changed during modify
modify.on('modifyend', function (e) {
  if (!modifySnapshot) return;
  const feature = e.features.getArray()[0];
  if (!feature) return;
  const newGeom = feature.getGeometry()?.clone() as Geometry | undefined;
  const newProps = { ...feature.getProperties() };
  const oldGeom = modifySnapshot.geometry;
  const oldProps = modifySnapshot.properties;
  modifySnapshot = null;

  if (!newGeom) return;

  // Compare geometry by serializing to WKT
  const wktFmt = new WKT();
  const changed = wktFmt.writeGeometry(newGeom) !== wktFmt.writeGeometry(oldGeom);
  if (!changed) return;

  history.record(new UpdateCommand(feature, oldGeom, oldProps, newGeom, newProps));
});

const typeInteraction = document.getElementById('interaction') as HTMLSelectElement;
const geometryType = document.getElementById('geometryType') as HTMLSelectElement;
const snapToggle = document.getElementById('snapToggle') as HTMLInputElement;
const drawOptions = document.getElementById('drawOptions') as HTMLElement;

function removeAllInteractions(): void {
  map.removeInteraction(select);
  map.removeInteraction(modify);
  if (draw) {
    map.removeInteraction(draw);
    draw = null;
  }
  if (snap) {
    map.removeInteraction(snap);
    snap = null;
  }
}

function ensureDrawInteraction(): void {
  removeAllInteractions();
  draw = new Draw({
    source: source,
    type: geometryType.value as any,
  });
  draw.on('drawend', function (e) {
    draw!.setActive(false);
    history.record(new InsertCommand(e.feature, source));
    const tabletxt = '<tr><td>'
      + '<input type="text" class="edit-fid" value="(自动生成)" readonly />' + '</td><td>'
      + '<input type="text" class="edit-name_py" value="name_py" />' + '</td><td>'
      + '<input type="text" class="edit-name_ch" value="name_ch" />' + '</td></tr>';
    $('#attributetbody').append(tabletxt);
  });
  map.addInteraction(draw);
  if (snapToggle.checked) {
    snap = new Snap({ source: source });
    map.addInteraction(snap);
  }
}

typeInteraction.onchange = function () {
  removeAllInteractions();

  if (typeInteraction.value === 'insert') {
    drawOptions.style.display = '';
    ensureDrawInteraction();
  } else {
    drawOptions.style.display = 'none';
  }

  if (typeInteraction.value === 'modify') {
    map.addInteraction(select);
    map.addInteraction(modify);
  }
};

geometryType.onchange = function () {
  if (typeInteraction.value === 'insert') {
    ensureDrawInteraction();
  }
};

snapToggle.onchange = function () {
  if (typeInteraction.value === 'insert') {
    ensureDrawInteraction();
  }
};

// WFS-T commit button
$('#creategml').click(function () {
  if (typeInteraction.value === 'search') {
    alert('支持 insert / modify / delete 操作');
    return;
  }

  const features = source.getFeatures();
  if (features.length === 0) {
    alert('当前没有可操作的要素，请先绘制或查询要素');
    return;
  }

  // Delete mode: apply DeleteCommand before building WFS-T
  if (typeInteraction.value === 'delete') {
    const feature = features[features.length - 1];
    const fid = feature.getId();
    if (!fid) {
      alert('删除操作需要要素有 fid，请先通过查看模式查询要素');
      return;
    }
    history.execute(new DeleteCommand(feature, source));
    sendWFSTransaction({
      insertFeatures: [],
      updateFeatures: [],
      deleteFeatures: [feature],
      baseUrl: baseurl,
    }).then(function () {
      history.clear();
      $('#attributetbody').empty();
      alert('提交成功');
    }).catch(function (err) {
      console.error('WFS-T 提交失败', err);
      alert('提交失败，请查看控制台信息');
    });
    return;
  }

  // Apply attribute table values for insert/modify
  if (typeInteraction.value === 'insert') {
    const feature = features[features.length - 1];
    const name_py = $('.edit-name_py').last().val();
    const name_ch = $('.edit-name_ch').last().val();
    feature.set('name_py', name_py);
    feature.set('name_ch', name_ch);
  }

  if (typeInteraction.value === 'modify') {
    const selectedFeatures = select.getFeatures().getArray();
    if (selectedFeatures.length === 0) {
      alert('请先在修改模式下选中一个要素');
      return;
    }
    const updateFeature = selectedFeatures[0];
    const name_py = $('.edit-name_py').last().val();
    const name_ch = $('.edit-name_ch').last().val();
    updateFeature.set('name_py', name_py);
    updateFeature.set('name_ch', name_ch);
  }

  // Batch: collect all features, classify by whether they have a fid
  const insertFeatures: Feature[] = [];
  const updateFeatures: Feature[] = [];
  features.forEach(function (f) {
    if (f.getId()) {
      updateFeatures.push(f);
    } else {
      insertFeatures.push(f);
    }
  });

  sendWFSTransaction({
    insertFeatures: insertFeatures,
    updateFeatures: updateFeatures,
    deleteFeatures: [],
    baseUrl: baseurl,
  }).then(function () {
    history.clear();
    $('#attributetbody').empty();
    alert('提交成功');
  }).catch(function (err) {
    console.error('WFS-T 提交失败', err);
    alert('提交失败，请查看控制台信息');
  });
});

// Immediate mode checkbox
const immediateMode = document.getElementById('immediateMode') as HTMLInputElement;

// Auto-submit on history change when immediate mode is on
history.onChange = function () {
  if (!immediateMode.checked) return;
  if (history.length === 0) return;
  const features = source.getFeatures();
  if (features.length === 0) return;
  const ins: Feature[] = [];
  const upd: Feature[] = [];
  features.forEach(function (f) {
    if (f.getId()) { upd.push(f); } else { ins.push(f); }
  });
  sendWFSTransaction({
    insertFeatures: ins,
    updateFeatures: upd,
    deleteFeatures: [],
    baseUrl: baseurl,
  }).then(function () {
    history.clear();
    $('#attributetbody').empty();
    alert('提交成功');
  }).catch(function (err) {
    console.error('WFS-T 提交失败', err);
    alert('提交失败，请查看控制台信息');
  });
};

// Undo / Redo buttons
$('#undoBtn').click(function () { history.undo(); });
$('#redoBtn').click(function () { history.redo(); });

// Keyboard shortcuts: Ctrl+Z undo, Ctrl+Y redo
$(document).on('keydown', function (e: any) {
  if (e.ctrlKey && e.key === 'z') { e.preventDefault(); history.undo(); }
  if (e.ctrlKey && e.key === 'y') { e.preventDefault(); history.redo(); }
});

// GetFeatureInfo on map click (search mode)
$('#map').click(function (e: any) {
  if (typeInteraction.value !== 'search') {
    return;
  }

  const t4326 = map.getEventCoordinate(e.originalEvent || e);
  const url4326 = baseurl + 'geoserver/wms?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&FORMAT=image%2Fpng&TRANSPARENT=true&QUERY_LAYERS=mapgis%3Av6_time_pref_pgn_utf_wgs84_geoserver&LAYERS=mapgis%3Av6_time_pref_pgn_utf_wgs84_geoserver&exceptions=application%2Fvnd.ogc.se_inimage&INFO_FORMAT=application/json&FEATURE_COUNT=50&X=50&Y=50&SRS=EPSG%3A4326&STYLES=&WIDTH=101&HEIGHT=101&BBOX=' + (t4326[0] - 0.0001).toString() + '%2C' + (t4326[1] - 0.0001).toString() + '%2C' + (t4326[0] + 0.0001).toString() + '%2C' + (t4326[1] + 0.0001).toString();

  $.ajax({
    url: url4326,
    type: 'GET',
    dataType: 'json',
    success: function (data: any) {
      if (!data.features || data.features.length === 0) {
        alert('该位置没有查询到要素');
        return;
      }
      source.clear();
      const features = new GeoJSON().readFeatures(data);
      source.addFeature(features[0]);
      $('#attributetbody').empty();
      const fid = data.features[0].id;
      const properties = data.features[0].properties;
      const name_py = properties.name_py || '';
      const name_ch = properties.name_ch || '';
      const tabletxt = '<tr><td>'
        + '<input type="text" class="edit-fid" value="' + fid + '" readonly />' + '</td><td>'
        + '<input type="text" class="edit-name_py" value="' + name_py + '" />' + '</td><td>'
        + '<input type="text" class="edit-name_ch" value="' + name_ch + '" />' + '</td></tr>';
      $('#attributetbody').append(tabletxt);
    },
    error: function (data: any) {
      console.log('查询失败');
      console.log(data);
      alert('查询要素失败，请查看控制台信息');
    },
  });
});
