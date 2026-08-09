WooCommerce Product Creator - iOS Testing Guide 

WooCommerce Product Creator - iOS App Testing Guide 

App Version: Build 26 

Date: June 26, 2026 

Platform: iOS 

1. Prerequisites 

Before testing, ensure you have: 

- An iOS device or simulator with the app installed 
    

- A WooCommerce store with REST API enabled 
    

- WooCommerce API credentials (Consumer Key & Consumer Secret) 
    

- A QR code containing credentials in format: `URL|ConsumerKey|ConsumerSecret` 
    

- Internet connection 
    

- At least one product category created in WooCommerce 
    

2. Authentication & Login 

Test 2.1 - QR Code Login (Happy Path) 

1. Launch the app 
    

2. You should see the home screen with "WooCommerce Product Creator" title 
    

3. Tap "Scan QR Code to Connect" button 
    

4. Point camera at a valid QR code containing: `https://yourstore.com|ck_xxxxx|cs_xxxxx` 
    

5. Expected: Green success message "Connected successfully!", auto-navigate to Menu screen 
    

Test 2.2 - Invalid QR Code Format 

6. From home screen, tap "Scan QR Code to Connect" 
    

7. Scan a QR code that does NOT contain the pipe-separated format (e.g., a random URL) 
    

8. Expected: Red error message "Invalid QR code format" 
    

Test 2.3 - Invalid Credentials 

9. Scan a QR code with correct format but wrong API keys 
    

10. Expected: Red error message "Invalid credentials or connection failed" 
    

Test 2.4 - Auto-Login on Restart 

11. After a successful login, close the app completely 
    

12. Reopen the app 
    

13. Expected: App automatically navigates to Menu screen (credentials saved) 
    

Test 2.5 - Logout 

14. From Menu screen, tap "Logout" (red card at bottom) 
    

15. Expected: Returns to Home screen, credentials cleared 
    

16. Close and reopen app 
    

17. Expected: Home screen shown (not auto-logged in) 
    

18. Create Product 

Test 3.1 - Form Validation (Empty Fields) 

18. From Menu, tap "Create New Product" 
    

19. Without filling any fields, tap "Create Product" button 
    

20. Expected: Validation errors appear: 
    

- "Please enter product name" 
    

- "Please enter SKU" 
    

- "Please enter description" 
    

Test 3.2 - Create Product (Happy Path) 

21. Fill in the form: 
    

- Product Name: "Test Product 001" 
    

- SKU: "TEST-001" 
    

- Description: "This is a test product description" 
    

- Regular Price: "29.99" 
    

- Sale Price: "19.99" (optional) 
    

- Category: Select any category from dropdown 
    

- Status: "Draft" 
    

- Stock Status: "In Stock" 
    

22. Tap "Create Product" 
    

23. Expected: Green message "Product created successfully!", form clears 
    

24. Verify in WooCommerce admin that the product was created with correct data 
    

Test 3.3 - Create Product Without Prices 

25. Fill required fields (Name, SKU, Description, Category) 
    

26. Leave Regular Price and Sale Price empty 
    

27. Tap "Create Product" 
    

28. Expected: Product created successfully without prices 
    

Test 3.4 - Create Product as Published 

29. Fill all required fields 
    

30. Set Status to "Publish" 
    

31. Tap "Create Product" 
    

32. Expected: Product created and visible on the store front-end 
    

Test 3.5 - Category Required Check 

33. Fill all fields EXCEPT Category (leave dropdown unselected) 
    

34. Tap "Create Product" 
    

35. Expected: Error message "Please select a category" 
    

Test 3.6 - Stock Status Options 

36. Create three products, each with a different stock status: 
    

- "In Stock" 
    

- "Out of Stock" 
    

- "On Backorder" 
    

37. Expected: Each product has correct stock status in WooCommerce 
    

Test 3.7 - Double Submit Prevention 

38. Fill all required fields 
    

39. Tap "Create Product" 
    

40. Immediately try to tap "Create Product" again while loading 
    

41. Expected: Button is disabled during submission (shows loading spinner), only one product created 
    

Test 3.8 - Logout from Create Screen 

42. While on Create Product screen, tap "LogOut" in the top-right 
    

43. Expected: Returns to Home screen, logged out 
    

44. Image Management 

Test 4.1 - Add Image from Camera 

44. On Create Product form, tap "Add Image" 
    

45. Select "Take Photo" from the bottom sheet 
    

46. Take a photo 
    

47. Expected: Image appears in the images list with filename and preview 
    

Test 4.2 - Add Images from Gallery 

48. Tap "Add Image" 
    

49. Select "Choose from Gallery" 
    

50. Select multiple images 
    

51. Expected: All selected images appear in the list 
    

Test 4.3 - Featured Image Badge 

52. Add 2 or more images 
    

53. Expected: The FIRST image in the list shows a "FEATURED" badge 
    

54. This will be the product thumbnail in WooCommerce 
    

Test 4.4 - Reorder Images 

55. Add 3+ images 
    

56. Long-press the drag handle (icon on the right) of an image 
    

57. Drag it to a different position 
    

58. Expected: Image moves to new position, "FEATURED" badge updates to first image 
    

Test 4.5 - Delete Image 

59. Add an image 
    

60. Tap the red delete button on the image card 
    

61. Expected: Image removed from the list 
    

Test 4.6 - Create Product with Images 

62. Add 1-3 images, fill all required fields 
    

63. Tap "Create Product" 
    

64. Expected: Product created with images visible in WooCommerce admin 
    

65. Search & Edit Products 

Test 5.1 - Search Products 

65. From Menu, tap "Edit Existing Product" 
    

66. Type a product name in the search field 
    

67. Expected: Results appear after brief delay (300ms debounce), showing matching products 
    

Test 5.2 - Search by SKU 

68. In search field, type a known SKU 
    

69. Expected: Product with that SKU appears in results 
    

Test 5.3 - Filter by Status 

70. Change the Status dropdown to "Published" 
    

71. Expected: Only published products shown 
    

72. Change to "Draft" 
    

73. Expected: Only draft products shown 
    

74. Change back to "All" 
    

75. Expected: All products shown 
    

Test 5.4 - Filter by Category 

76. Select a specific category from the Category dropdown 
    

77. Expected: Only products in that category shown 
    

78. Change back to "All" 
    

79. Expected: All products shown 
    

Test 5.5 - No Results 

80. Search for a product name that doesn't exist (e.g., "xyznonexistent999") 
    

81. Expected: "No products found" message displayed 
    

Test 5.6 - Product Card Display 

82. View search results 
    

83. Expected: Each product card shows: 
    

- Thumbnail image (or placeholder) 
    

- Product name (bold) 
    

- SKU 
    

- Price (in green, if available) 
    

- Stock status badge (green "IN STOCK" or gray "OUT OF STOCK") 
    

Test 5.7 - Open Product for Editing 

84. Tap on a product from search results 
    

85. Expected: Edit screen opens with all product data pre-populated: 
    

- Product name 
    

- SKU 
    

- Description (read-only) 
    

- Regular price 
    

- Sale price 
    

- Category selected 
    

- Status selected 
    

- Stock status selected 
    

- Existing images displayed 
    

6. Edit Product 

Test 6.1 - Description is Read-Only 

86. Open a product for editing 
    

87. Look at the Description field 
    

88. Expected: Description shown as read-only text with info message "Use desktop to edit description" 
    

89. Cannot type or modify the description 
    

Test 6.2 - Update Product Name 

90. Open a product for editing 
    

91. Change the product name 
    

92. Tap "Update Product" 
    

93. Expected: Green message "Product updated successfully!", returns to search screen 
    

94. Search for the product to verify the name was updated 
    

Test 6.3 - Update Price 

95. Open a product, change the Regular Price 
    

96. Tap "Update Product" 
    

97. Expected: Price updated in WooCommerce 
    

Test 6.4 - Update Stock Status 

98. Open a product, change Stock Status from "In Stock" to "Out of Stock" 
    

99. Tap "Update Product" 
    

100. Expected: Stock status updated, reflected in search results 
    

Test 6.5 - Update Category 

101. Open a product, change the Category 
    

102. Tap "Update Product" 
    

103. Expected: Product moved to new category in WooCommerce 
    

Test 6.6 - Existing Images Displayed 

104. Open a product that has images 
    

105. Expected: All existing images shown with "Existing image" label and loaded from network 
    

Test 6.7 - Add New Image to Existing Product 

106. Open a product for editing 
    

107. Tap "Add Image" and add a new photo 
    

108. Tap "Update Product" 
    

109. Expected: New image added alongside existing images in WooCommerce 
    

Test 6.8 - Remove Image from Existing Product 

110. Open a product with images 
    

111. Tap the delete button on an existing image 
    

112. Tap "Update Product" 
    

113. Expected: Image removed from product in WooCommerce 
    

Test 6.9 - Back Button from Edit 

114. Open a product for editing 
    

115. Tap the back arrow (without saving) 
    

116. Expected: Returns to search screen, search results refreshed 
    

Test 6.10 - Attributes Not Modified 

117. Open a product that has attributes in WooCommerce 
    

118. Edit only the name or price 
    

119. Tap "Update Product" 
    

120. Expected: Product attributes remain unchanged in WooCommerce (attributes are not sent in update) 
    

121. Error Handling & Edge Cases 

Test 7.1 - No Internet Connection 

121. Turn off WiFi/mobile data 
    

122. Try to create a product 
    

123. Expected: Red error message about connection failure 
    

Test 7.2 - Network Recovery 

124. With no internet, attempt an action (will fail) 
    

125. Turn internet back on 
    

126. Retry the action 
    

127. Expected: Action succeeds 
    

Test 7.3 - Rapid Search Input 

128. In search screen, type quickly (multiple characters fast) 
    

129. Expected: Search doesn't fire for every keystroke (debounce), only searches after you stop typing 
    

Test 7.4 - Large Image Upload 

130. Take a high-resolution photo from camera 
    

131. Create a product with this image 
    

132. Expected: Image is compressed (quality 80) and uploaded successfully 
    

Test 7.5 - Duplicate SKU 

133. Create a product with SKU "DUPLICATE-001" 
    

134. Try to create another product with the same SKU 
    

135. Expected: Error from WooCommerce about duplicate SKU displayed in red SnackBar 
    

Test 7.6 - Special Characters in Fields 

136. Create a product with special characters in name: `Test "Product" & <Special> 'Chars'` 
    

137. Expected: Product created successfully, characters preserved 
    

138. UI & Visual Checks 

Test 8.1 - Dark Theme 

138. Navigate through all screens 
    

139. Expected: Dark background with orange accent color throughout 
    

Test 8.2 - Loading Indicators 

140. Perform any API action (create, search, etc.) 
    

141. Expected: Loading spinner visible while waiting for response 
    

Test 8.3 - Keyboard Behavior 

142. Tap on text fields 
    

143. Expected: Keyboard appears, form scrolls to keep field visible 
    

144. Tap outside the field or press Done 
    

145. Expected: Keyboard dismisses 
    

Test 8.4 - Price Keyboard 

146. Tap on Regular Price or Sale Price field 
    

147. Expected: Numeric keyboard appears (with decimal point) 
    

Test 8.5 - All Screens Accessible 

148. Navigate: Home -> Menu -> Create -> Back -> Menu -> Search -> Edit -> Back -> Menu -> Logout -> Home 
    

149. Expected: All navigation transitions work smoothly, no crashes 
    

150. Quick Smoke Test Checklist 

For a quick validation of core functionality: 

- [ ] App launches without crash 
    

- [ ] QR code scan works and connects to store 
    

- [ ] Create Product screen opens and shows all fields 
    

- [ ] Can create a product with name, SKU, description, and category 
    

- [ ] Product appears in WooCommerce admin 
    

- [ ] Can take photo and attach to product 
    

- [ ] Can search for products 
    

- [ ] Can open and edit a product 
    

- [ ] Description is read-only in edit mode 
    

- [ ] Update saves changes 
    

- [ ] Logout works and clears session 
    

- [ ] App auto-connects on restart (when logged in) 
    

10. Test Results Log 

| Test ID | Description | Pass/Fail | Notes | Tester | Date | 

|---------|-------------|-----------|-------|--------|------| 

| 2.1 | QR Code Login | | | | | 

| 2.2 | Invalid QR Format | | | | | 

| 2.3 | Invalid Credentials | | | | | 

| 2.4 | Auto-Login | | | | | 

| 2.5 | Logout | | | | | 

| 3.1 | Form Validation | | | | | 

| 3.2 | Create Product | | | | | 

| 3.3 | Create Without Prices | | | | | 

| 3.4 | Create as Published | | | | | 

| 3.5 | Category Required | | | | | 

| 3.6 | Stock Status Options | | | | | 

| 3.7 | Double Submit | | | | | 

| 3.8 | Logout from Create | | | | | 

| 4.1 | Camera Image | | | | | 

| 4.2 | Gallery Images | | | | | 

| 4.3 | Featured Badge | | | | | 

| 4.4 | Reorder Images | | | | | 

| 4.5 | Delete Image | | | | | 

| 4.6 | Create with Images | | | | | 

| 5.1 | Search Products | | | | | 

| 5.2 | Search by SKU | | | | | 

| 5.3 | Filter by Status | | | | | 

| 5.4 | Filter by Category | | | | | 

| 5.5 | No Results | | | | | 

| 5.6 | Product Card Display | | | | | 

| 5.7 | Open for Editing | | | | | 

| 6.1 | Description Read-Only | | | | | 

| 6.2 | Update Name | | | | | 

| 6.3 | Update Price | | | | | 

| 6.4 | Update Stock Status | | | | | 

| 6.5 | Update Category | | | | | 

| 6.6 | Existing Images | | | | | 

| 6.7 | Add Image to Existing | | | | | 

| 6.8 | Remove Image | | | | | 

| 6.9 | Back without Save | | | | | 

| 6.10 | Attributes Unchanged | | | | | 

| 7.1 | No Internet | | | | | 

| 7.2 | Network Recovery | | | | | 

| 7.3 | Rapid Search | | | | | 

| 7.4 | Large Image | | | | | 

| 7.5 | Duplicate SKU | | | | | 

| 7.6 | Special Characters | | | | | 

| 8.1 | Dark Theme | | | | | 

| 8.2 | Loading Indicators | | | | | 

| 8.3 | Keyboard Behavior | | | | | 

| 8.4 | Price Keyboard | | | | | 

| 8.5 | Navigation Flow | | | | | 

End of Testing Guide