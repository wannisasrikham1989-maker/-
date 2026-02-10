// สร้าง Admin User ผ่าน Firebase Admin SDK
// รันด้วย: node create_admin_user.js

const firebaseAdmin = require('firebase-admin');
const serviceAccount = require('./service-account-key.json'); // ต้องดาวน์โหลดจาก Firebase Console

firebaseAdmin.initializeApp({
  credential: firebaseAdmin.credential.cert(serviceAccount)
});

async function createAdminUser(email, password, fullName) {
  try {
    // สร้าง user ใน Firebase Auth
    const userRecord = await firebaseAdmin.auth().createUser({
      email: email,
      password: password,
      displayName: fullName
    });

    // สร้าง user document ใน Firestore พร้อม role admin
    await firebaseAdmin.firestore().collection('users').doc(userRecord.uid).set({
      email: email,
      fullName: fullName,
      role: 'admin',
      createdAt: firebaseAdmin.firestore.FieldValue.serverTimestamp()
    });

    console.log('✅ สร้าง admin user สำเร็จ:');
    console.log('   Email:', email);
    console.log('   UID:', userRecord.uid);
  } catch (error) {
    console.error('❌ เกิดข้อผิดพลาด:', error.message);
  }
}

// รันฟังก์ชัน
createAdminUser('admin@example.com', 'admin123456', 'ผู้ดูแลระบบ');
