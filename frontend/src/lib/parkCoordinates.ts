// Static coordinates for National Parks
// These coordinates represent the approximate center of each park
export const PARK_COORDINATES: Record<string, { lat: number; lng: number; }> = {
  // Major National Parks
  'YELL': { lat: 44.428, lng: -110.588 }, // Yellowstone
  'GRCA': { lat: 36.1069, lng: -112.1129 }, // Grand Canyon
  'YOSE': { lat: 37.8651, lng: -119.5383 }, // Yosemite
  'ZION': { lat: 37.2982, lng: -113.0263 }, // Zion
  'ACAD': { lat: 44.35, lng: -68.21 }, // Acadia
  'ARCH': { lat: 38.68, lng: -109.57 }, // Arches
  'ROMO': { lat: 40.4, lng: -105.58 }, // Rocky Mountain
  'GRSM': { lat: 35.6117, lng: -83.4895 }, // Great Smoky Mountains
  'OLYM': { lat: 47.8021, lng: -123.6044 }, // Olympic
  'GLAC': { lat: 48.7596, lng: -113.787 }, // Glacier
  
  // National Monuments & Historic Sites
  'DEVA': { lat: 36.5054, lng: -117.0794 }, // Death Valley
  'JOTR': { lat: 33.8734, lng: -115.901 }, // Joshua Tree
  'BAND': { lat: 35.7781, lng: -106.2708 }, // Bandelier
  'CACO': { lat: 42.0699, lng: -70.0464 }, // Cape Cod
  'STLI': { lat: 40.6892, lng: -74.0445 }, // Statue of Liberty
  
  // National Recreation Areas
  'GLEN': { lat: 37.0042, lng: -111.1892 }, // Glen Canyon
  'LAME': { lat: 36.0905, lng: -114.7366 }, // Lake Mead
  'CURE': { lat: 38.4619, lng: -107.1817 }, // Curecanti
  
  // National Seashores
  'CAHA': { lat: 35.2590, lng: -75.5277 }, // Cape Hatteras
  'ASIS': { lat: 38.0593, lng: -75.1458 }, // Assateague Island
  
  // Historical Parks
  'INDE': { lat: 39.9496, lng: -75.1503 }, // Independence
  'COLO': { lat: 37.2707, lng: -76.6135 }, // Colonial
  'BOST': { lat: 42.3601, lng: -71.0589 }, // Boston
  'GETT': { lat: 39.8309, lng: -77.2361 }, // Gettysburg
  'ANTI': { lat: 39.4618, lng: -77.7311 }, // Antietam
  
  // Additional Parks
  'BRCA': { lat: 37.5930, lng: -112.1871 }, // Bryce Canyon
  'CANY': { lat: 38.2, lng: -109.93 }, // Canyonlands
  'CARE': { lat: 38.0877, lng: -111.1660 }, // Capitol Reef
  'REDW': { lat: 41.2132, lng: -124.0046 }, // Redwood
  'SHEN': { lat: 38.2928, lng: -78.6795 }, // Shenandoah
  'BADL': { lat: 43.8554, lng: -101.9777 }, // Badlands
  'EVER': { lat: 25.2866, lng: -80.8987 }, // Everglades
  'ABLI': { lat: 37.5429, lng: -85.6739 }, // Abraham Lincoln Birthplace
  'ADAM': { lat: 42.2553, lng: -71.0275 }, // Adams
  'AFBG': { lat: 40.7150, lng: -74.0042 }, // African Burial Ground
  'AGFO': { lat: 42.4186, lng: -103.7273 }, // Agate Fossil Beds
  'ALFL': { lat: 35.5669, lng: -101.6719 }, // Alibates Flint Quarries
  'AMIS': { lat: 29.5255, lng: -101.0769 }, // Amistad
  'ANIA': { lat: 56.8987, lng: -158.6114 }, // Aniakchak
  'APCO': { lat: 37.3760, lng: -78.7959 }, // Appomattox Court House
  'AZRU': { lat: 36.8389, lng: -107.9983 }, // Aztec Ruins
  'BEPA': { lat: 38.9072, lng: -77.0369 }, // Belmont-Paul Women's Equality
  'BIBE': { lat: 29.1275, lng: -103.2425 }, // Big Bend
  'BICA': { lat: 45.0293, lng: -108.1618 }, // Bighorn Canyon
  'BICR': { lat: 33.5186, lng: -86.8104 }, // Birmingham Civil Rights
  'BISC': { lat: 25.4390, lng: -80.4017 }, // Biscayne
  'BLCA': { lat: 38.5753, lng: -107.7018 }, // Black Canyon of the Gunnison
  'BLRV': { lat: 42.1341, lng: -71.1636 }, // Blackstone River Valley
  'BOWA': { lat: 37.1214, lng: -79.9081 }, // Booker T Washington
  'BOHA': { lat: 42.3398, lng: -70.9661 }, // Boston Harbor Islands
  'BRVB': { lat: 39.0409, lng: -95.6890 }, // Brown v. Board of Education
  'BUIS': { lat: 17.7539, lng: -64.6255 }, // Buck Island Reef
  'CABR': { lat: 32.6722, lng: -117.2417 }, // Cabrillo
  'CANE': { lat: 37.7862, lng: -84.5985 }, // Camp Nelson
  'CANA': { lat: 28.8123, lng: -80.8101 }, // Canaveral
  'CARI': { lat: 31.0407, lng: -93.0096 }, // Cane River Creole
  'CACH': { lat: 36.1490, lng: -109.3389 }, // Canyon de Chelly
  'CALO': { lat: 34.6204, lng: -76.5197 }, // Cape Lookout
  'CAVO': { lat: 36.7828, lng: -103.9705 }, // Capulin Volcano
  'CIBS': { lat: 40.2019, lng: -77.1956 }, // Carlisle Federal Indian Boarding School
  'CAVE': { lat: 32.1478, lng: -104.5567 }, // Carlsbad Caverns
  'CAGR': { lat: 32.4797, lng: -111.5375 }, // Casa Grande Ruins
  'CASA': { lat: 29.8974, lng: -81.3123 }, // Castillo de San Marcos
  'CACL': { lat: 40.7033, lng: -74.0170 }, // Castle Clinton
  'CAMO': { lat: 35.2917, lng: -115.0881 }, // Castle Mountains
  'CEBR': { lat: 37.6283, lng: -112.8453 }, // Cedar Breaks
  'CEBE': { lat: 39.0052, lng: -78.3086 }, // Cedar Creek & Belle Grove
  'CAME': { lat: 36.9212, lng: -76.0051 }, // Cape Henry Memorial
  'CAKR': { lat: 67.4162, lng: -163.1524 }, // Cape Krusenstern
  'CHCU': { lat: 36.0544, lng: -107.9914 }, // Chaco Culture
  'CHIS': { lat: 34.0069, lng: -119.7785 }, // Channel Islands
}; 