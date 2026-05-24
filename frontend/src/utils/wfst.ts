import WFS from 'ol/format/WFS';
import type Feature from 'ol/Feature';

export interface WFSTransactionParams {
  insertFeatures: Feature[];
  updateFeatures: Feature[];
  deleteFeatures: Feature[];
  baseUrl: string;
}

export function sendWFSTransaction(params: WFSTransactionParams): Promise<void> {
  const { insertFeatures, updateFeatures, deleteFeatures, baseUrl } = params;

  if (insertFeatures.length === 0 && updateFeatures.length === 0 && deleteFeatures.length === 0) {
    return Promise.reject(new Error('没有待提交的操作'));
  }

  const wfstSerializer = new WFS();
  const featObject: Node = wfstSerializer.writeTransaction(
    insertFeatures,
    updateFeatures,
    deleteFeatures,
    {
      featureNS: 'http://geoserver/mapgis',
      featurePrefix: 'mapgis',
      featureType: 'v6_time_pref_pgn_utf_wgs84_geoserver',
      srsName: 'EPSG:4326',
      nativeElements: [],
    },
  );

  const serializer = new XMLSerializer();
  const featString = serializer.serializeToString(featObject);
  console.log('WFS-T XML:', featString);

  return fetch(baseUrl + 'geoserver/wfs', {
    method: 'POST',
    headers: { 'Content-Type': 'text/xml' },
    body: featString,
  }).then((response) => {
    if (!response.ok) {
      throw new Error(`WFS-T 提交失败: ${response.status} ${response.statusText}`);
    }
    return response.text();
  }).then((data) => {
    console.log('WFS-T 提交成功', data);
  });
}
