// เพิ่มหมวดหมู่เริ่มต้น
// รันด้วย: node init_categories.js

const firebaseAdmin = require('firebase-admin');
const serviceAccount = require('./service-account-key.json');

firebaseAdmin.initializeApp({
  credential: firebaseAdmin.credential.cert(serviceAccount)
});

const categories = [
  'คอมพิวเตอร์',
  'เก้าอี้',
  'เคส',
  'โน้ตบุ๊ค'
];

async function initCategories() {
  const db = firebaseAdmin.firestore();
  const batch = db.batch();
  
  categories.forEach(name => {
    const docRef = db.collection('categories').doc();
    batch.set(docRef, {
      name: name,
      createdAt: firebaseAdmin.firestore.FieldValue.serverTimestamp()
    });
  });
  
  await batch.commit();
  console.log('✅ เพิ่มหมวดหมู่สำเร็จ:', categories);
}

initCategories().catch(console.error);
