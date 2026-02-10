// Firebase Service - ฟังก์ชันสำหรับทำงานกับ Firebase

// ตรวจสอบสถานะล็อกอิน
function checkAuthState(callback) {
    auth.onAuthStateChanged(async (user) => {
        if (user) {
            // ดึงข้อมูล user จาก Firestore
            try {
                const userDoc = await db.collection('users').doc(user.uid).get();
                if (userDoc.exists) {
                    const userData = userDoc.data();
                    callback({
                        authenticated: true,
                        user: {
                            id: user.uid,
                            email: user.email,
                            ...userData
                        }
                    });
                } else {
                    callback({ authenticated: true, user: { id: user.uid, email: user.email } });
                }
            } catch (error) {
                console.error('Error fetching user data:', error);
                callback({ authenticated: true, user: { id: user.uid, email: user.email } });
            }
        } else {
            callback({ authenticated: false });
        }
    });
}

// เข้าสู่ระบบด้วย email/password
async function loginWithEmail(email, password) {
    try {
        const userCredential = await auth.signInWithEmailAndPassword(email, password);
        const userDoc = await db.collection('users').doc(userCredential.user.uid).get();
        let userData = { id: userCredential.user.uid, email: userCredential.user.email };
        
        if (userDoc.exists) {
            userData = { ...userData, ...userDoc.data() };
        }
        
        return { success: true, user: userData };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ลงทะเบียนผู้ใช้ใหม่
async function registerUser(email, password, fullName, role = 'user') {
    try {
        const userCredential = await auth.createUserWithEmailAndPassword(email, password);
        
        // บันทึกข้อมูล user ใน Firestore
        await db.collection('users').doc(userCredential.user.uid).set({
            email: email,
            fullName: fullName,
            role: role,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        
        return { 
            success: true, 
            user: { 
                id: userCredential.user.uid, 
                email: email,
                fullName: fullName,
                role: role
            } 
        };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ออกจากระบบ
async function logout() {
    try {
        await auth.signOut();
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ==================== Equipment Functions ====================

// ดึงข้อมูลครุภัณฑ์ทั้งหมด
async function getAllEquipment() {
    try {
        const snapshot = await db.collection('equipment').orderBy('createdAt', 'desc').get();
        return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
        console.error('Error getting equipment:', error);
        return [];
    }
}

// เพิ่มครุภัณฑ์ใหม่
async function addEquipment(data) {
    try {
        const docRef = await db.collection('equipment').add({
            ...data,
            createdAt: firebase.firestore.FieldValue.serverTimestamp(),
            status: 'available'
        });
        return { success: true, id: docRef.id };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// แก้ไขครุภัณฑ์
async function updateEquipment(id, data) {
    try {
        await db.collection('equipment').doc(id).update({
            ...data,
            updatedAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ลบครุภัณฑ์
async function deleteEquipment(id) {
    try {
        await db.collection('equipment').doc(id).delete();
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ขายครุภัณฑ์ (ลบและบันทึกประวัติการขาย)
async function sellEquipment(id, equipmentData, price) {
    try {
        const batch = db.batch();
        
        // บันทึกประวัติการขาย
        const salesRef = db.collection('sales_history').doc();
        batch.set(salesRef, {
            equipmentId: id,
            equipmentName: equipmentData.name,
            equipmentCategory: equipmentData.category,
            price: price,
            soldAt: firebase.firestore.FieldValue.serverTimestamp(),
            soldBy: auth.currentUser?.uid || 'unknown'
        });
        
        // ลบครุภัณฑ์
        const equipmentRef = db.collection('equipment').doc(id);
        batch.delete(equipmentRef);
        
        await batch.commit();
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ยืมครุภัณฑ์
async function borrowEquipment(equipmentId, userId) {
    try {
        await db.collection('equipment').doc(equipmentId).update({
            status: 'borrowed',
            borrowerId: userId,
            borrowedAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        
        // บันทึกประวัติการยืม
        await db.collection('borrow_history').add({
            equipmentId: equipmentId,
            userId: userId,
            action: 'borrow',
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        });
        
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// คืนครุภัณฑ์
async function returnEquipment(equipmentId, userId) {
    try {
        await db.collection('equipment').doc(equipmentId).update({
            status: 'available',
            borrowerId: null,
            returnedAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        
        // บันทึกประวัติการคืน
        await db.collection('borrow_history').add({
            equipmentId: equipmentId,
            userId: userId,
            action: 'return',
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        });
        
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ==================== Categories Functions ====================

// ดึงหมวดหมู่ทั้งหมด
async function getAllCategories() {
    try {
        const snapshot = await db.collection('categories').orderBy('name').get();
        return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
        console.error('Error getting categories:', error);
        return [];
    }
}

// เพิ่มหมวดหมู่
async function addCategory(name) {
    try {
        const docRef = await db.collection('categories').add({
            name: name,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        });
        return { success: true, id: docRef.id };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// ==================== History Functions ====================

// ดึงประวัติการยืม-คืน
async function getBorrowHistory() {
    try {
        const snapshot = await db.collection('borrow_history')
            .orderBy('timestamp', 'desc')
            .limit(100)
            .get();
        return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
        console.error('Error getting borrow history:', error);
        return [];
    }
}

// ดึงประวัติการขาย
async function getSalesHistory() {
    try {
        const snapshot = await db.collection('sales_history')
            .orderBy('soldAt', 'desc')
            .limit(100)
            .get();
        return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
        console.error('Error getting sales history:', error);
        return [];
    }
}

// ดึงครุภัณฑ์ที่ยืมค้าง
async function getOverdueEquipment() {
    try {
        const snapshot = await db.collection('equipment')
            .where('status', '==', 'borrowed')
            .get();
        return snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    } catch (error) {
        console.error('Error getting overdue equipment:', error);
        return [];
    }
}

// ดึงข้อมูล dashboard stats
async function getDashboardStats() {
    try {
        const equipment = await getAllEquipment();
        const overdue = await getOverdueEquipment();
        const sales = await getSalesHistory();
        
        return {
            totalEquipment: equipment.length,
            borrowed: equipment.filter(e => e.status === 'borrowed').length,
            available: equipment.filter(e => e.status === 'available').length,
            overdueCount: overdue.length,
            totalSales: sales.length,
            totalRevenue: sales.reduce((sum, s) => sum + (s.price || 0), 0)
        };
    } catch (error) {
        console.error('Error getting dashboard stats:', error);
        return {
            totalEquipment: 0,
            borrowed: 0,
            available: 0,
            overdueCount: 0,
            totalSales: 0,
            totalRevenue: 0
        };
    }
}
