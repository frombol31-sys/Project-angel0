--[=[
 d888b  db    db d888888b      .d888b.      db      db    db  .d8b.  
88' Y8b 88    88   `88'        VP  `8D      88      88    88 d8' `8b 
88      88    88    88            odD'      88      88    88 88ooo88 
88  ooo 88    88    88          .88'        88      88    88 88~~~88 
88. ~8~ 88b  d88   .88.        j88.         88booo. 88b  d88 88   88    @uniquadev
 Y888P  ~Y8888P' Y888888P      888888D      Y88888P ~Y8888P' YP   YP  CONVERTER 

designed using localmaze gui creator
]=]

local LMG2L = {};

LMG2L["ScreenGui_1"] = Instance.new("ScreenGui", game:GetService("Players").LocalPlayer:WaitForChild("PlayerGui"));
LMG2L["ScreenGui_1"]["ZIndexBehavior"] = Enum.ZIndexBehavior.Sibling;


LMG2L["Frame_2"] = Instance.new("Frame", LMG2L["ScreenGui_1"]);
LMG2L["Frame_2"]["BorderSizePixel"] = 0;
LMG2L["Frame_2"]["BackgroundColor3"] = Color3.fromRGB(255, 255, 255);
LMG2L["Frame_2"]["Size"] = UDim2.new(0.6225, 0, 0.73596, 0);
LMG2L["Frame_2"]["Position"] = UDim2.new(0.14896, 0, 0.06074, 0);


LMG2L["Close_3"] = Instance.new("TextButton", LMG2L["Frame_2"]);
LMG2L["Close_3"]["BorderSizePixel"] = 0;
LMG2L["Close_3"]["TextColor3"] = Color3.fromRGB(255, 255, 255);
LMG2L["Close_3"]["BackgroundColor3"] = Color3.fromRGB(255, 0, 0);
LMG2L["Close_3"]["Size"] = UDim2.new(0.03502, 0, 0.06618, 0);
LMG2L["Close_3"]["Text"] = [[X]];
LMG2L["Close_3"]["Name"] = [[Close]];
LMG2L["Close_3"]["Position"] = UDim2.new(0.95331, 0, 0.01471, 0);


LMG2L["UICorner_4"] = Instance.new("UICorner", LMG2L["Close_3"]);



LMG2L["LocalScript_5"] = Instance.new("LocalScript", LMG2L["Close_3"]);



LMG2L["Execute_6"] = Instance.new("TextButton", LMG2L["Frame_2"]);
LMG2L["Execute_6"]["BorderSizePixel"] = 0;
LMG2L["Execute_6"]["TextColor3"] = Color3.fromRGB(255, 255, 255);
LMG2L["Execute_6"]["BackgroundColor3"] = Color3.fromRGB(204, 204, 204);
LMG2L["Execute_6"]["Size"] = UDim2.new(0.09728, 0, 0.35294, 0);
LMG2L["Execute_6"]["Text"] = [[EXE]];
LMG2L["Execute_6"]["Name"] = [[Execute]];
LMG2L["Execute_6"]["Position"] = UDim2.new(0.75097, 0, 0.09559, 0);


LMG2L["UICorner_7"] = Instance.new("UICorner", LMG2L["Execute_6"]);



LMG2L["LocalScript_8"] = Instance.new("LocalScript", LMG2L["Execute_6"]);



LMG2L["Project_9"] = Instance.new("TextLabel", LMG2L["Frame_2"]);
LMG2L["Project_9"]["BorderSizePixel"] = 0;
LMG2L["Project_9"]["BackgroundColor3"] = Color3.fromRGB(255, 255, 255);
LMG2L["Project_9"]["Size"] = UDim2.new(0.14056, 0, 0.03817, 0);
LMG2L["Project_9"]["Text"] = [[Project H!!dd3 (client side)]];
LMG2L["Project_9"]["Name"] = [[Project]];
LMG2L["Project_9"]["Position"] = UDim2.new(0.06702, 0, 0.01471, 0);


LMG2L["Clear_a"] = Instance.new("TextButton", LMG2L["Frame_2"]);
LMG2L["Clear_a"]["BorderSizePixel"] = 0;
LMG2L["Clear_a"]["TextColor3"] = Color3.fromRGB(255, 255, 255);
LMG2L["Clear_a"]["BackgroundColor3"] = Color3.fromRGB(204, 204, 204);
LMG2L["Clear_a"]["Size"] = UDim2.new(0.09728, 0, 0.28676, 0);
LMG2L["Clear_a"]["Text"] = [[CLEAR]];
LMG2L["Clear_a"]["Name"] = [[Clear]];
LMG2L["Clear_a"]["Position"] = UDim2.new(0.75097, 0, 0.46324, 0);


LMG2L["UICorner_b"] = Instance.new("UICorner", LMG2L["Clear_a"]);



LMG2L["LocalScript_c"] = Instance.new("LocalScript", LMG2L["Clear_a"]);



LMG2L["C00l_d"] = Instance.new("TextButton", LMG2L["Frame_2"]);
LMG2L["C00l_d"]["TextWrapped"] = true;
LMG2L["C00l_d"]["BorderSizePixel"] = 0;
LMG2L["C00l_d"]["TextScaled"] = true;
LMG2L["C00l_d"]["BackgroundColor3"] = Color3.fromRGB(190, 0, 0);
LMG2L["C00l_d"]["Size"] = UDim2.new(0.05447, 0, 0.11029, 0);
LMG2L["C00l_d"]["Text"] = [[C00lgui]];
LMG2L["C00l_d"]["Name"] = [[C00l]];
LMG2L["C00l_d"]["Position"] = UDim2.new(0.75097, 0, 0.76471, 0);


LMG2L["UICorner_e"] = Instance.new("UICorner", LMG2L["C00l_d"]);



LMG2L["LocalScript_f"] = Instance.new("LocalScript", LMG2L["C00l_d"]);



LMG2L["ImageLabel_10"] = Instance.new("ImageLabel", LMG2L["Frame_2"]);
LMG2L["ImageLabel_10"]["BorderSizePixel"] = 0;
LMG2L["ImageLabel_10"]["BackgroundColor3"] = Color3.fromRGB(255, 255, 255);
-- LMG2L["ImageLabel_10"]["ImageContent"] = ;
LMG2L["ImageLabel_10"]["Image"] = [[rbxassetid://133303526215056]];
LMG2L["ImageLabel_10"]["Size"] = UDim2.new(0.03614, 0, 0.05344, 0);
LMG2L["ImageLabel_10"]["Position"] = UDim2.new(0.26698, 0, 0.01471, 0);


LMG2L["UICorner_11"] = Instance.new("UICorner", LMG2L["Frame_2"]);



LMG2L["LocalScript2_12"] = Instance.new("LocalScript", LMG2L["Frame_2"]);
LMG2L["LocalScript2_12"]["Name"] = [[LocalScript2]];


LMG2L["TextLabel_13"] = Instance.new("TextLabel", LMG2L["Frame_2"]);
LMG2L["TextLabel_13"]["TextWrapped"] = true;
LMG2L["TextLabel_13"]["BorderSizePixel"] = 0;
LMG2L["TextLabel_13"]["TextScaled"] = true;
LMG2L["TextLabel_13"]["BackgroundColor3"] = Color3.fromRGB(255, 255, 255);
LMG2L["TextLabel_13"]["BackgroundTransparency"] = 1;
LMG2L["TextLabel_13"]["Size"] = UDim2.new(0.54864, 0, 0.21324, 0);
LMG2L["TextLabel_13"]["Text"] = [[Welcome exploiter ]];
LMG2L["TextLabel_13"]["Position"] = UDim2.new(0.06226, 0, 0.75735, 0);


LMG2L["RO_14"] = Instance.new("TextButton", LMG2L["Frame_2"]);
LMG2L["RO_14"]["TextWrapped"] = true;
LMG2L["RO_14"]["BorderSizePixel"] = 0;
LMG2L["RO_14"]["TextScaled"] = true;
LMG2L["RO_14"]["TextColor3"] = Color3.fromRGB(255, 255, 255);
LMG2L["RO_14"]["BackgroundColor3"] = Color3.fromRGB(65, 0, 208);
LMG2L["RO_14"]["Size"] = UDim2.new(0.05447, 0, 0.11029, 0);
LMG2L["RO_14"]["Text"] = [[Roxploit 6.0]];
LMG2L["RO_14"]["Name"] = [[RO]];
LMG2L["RO_14"]["Position"] = UDim2.new(0.82879, 0, 0.76471, 0);


LMG2L["UICorner_15"] = Instance.new("UICorner", LMG2L["RO_14"]);



LMG2L["LocalScript_16"] = Instance.new("LocalScript", LMG2L["RO_14"]);



LMG2L["R6_17"] = Instance.new("TextButton", LMG2L["Frame_2"]);
LMG2L["R6_17"]["BorderSizePixel"] = 0;
LMG2L["R6_17"]["TextColor3"] = Color3.fromRGB(255, 255, 255);
LMG2L["R6_17"]["BackgroundColor3"] = Color3.fromRGB(204, 204, 204);
LMG2L["R6_17"]["Size"] = UDim2.new(0.07782, 0, 0.07353, 0);
LMG2L["R6_17"]["Text"] = [[R6]];
LMG2L["R6_17"]["Name"] = [[R6]];
LMG2L["R6_17"]["Position"] = UDim2.new(0.92218, 0, 0.10294, 0);


LMG2L["UICorner_18"] = Instance.new("UICorner", LMG2L["R6_17"]);



LMG2L["LocalScript_19"] = Instance.new("LocalScript", LMG2L["R6_17"]);



LMG2L["TextBox_1a"] = Instance.new("TextBox", LMG2L["Frame_2"]);
LMG2L["TextBox_1a"]["BorderSizePixel"] = 0;
LMG2L["TextBox_1a"]["TextWrapped"] = true;
LMG2L["TextBox_1a"]["TextColor3"] = Color3.fromRGB(255, 255, 255);
LMG2L["TextBox_1a"]["TextScaled"] = true;
LMG2L["TextBox_1a"]["BackgroundColor3"] = Color3.fromRGB(139, 139, 139);
LMG2L["TextBox_1a"]["FontFace"] = Font.new([[rbxasset://fonts/families/GothamSSm.json]], Enum.FontWeight.Medium, Enum.FontStyle.Normal);
LMG2L["TextBox_1a"]["Size"] = UDim2.new(0.71984, 0, 0.66912, 0);
LMG2L["TextBox_1a"]["Position"] = UDim2.new(0.01556, 0, 0.07353, 0);
LMG2L["TextBox_1a"]["Text"] = [[script]];


LMG2L["UICorner_1b"] = Instance.new("UICorner", LMG2L["TextBox_1a"]);



LMG2L["LocalScript_1c"] = Instance.new("LocalScript", LMG2L["Frame_2"]);



LMG2L["RE_1d"] = Instance.new("TextButton", LMG2L["Frame_2"]);
LMG2L["RE_1d"]["BorderSizePixel"] = 0;
LMG2L["RE_1d"]["TextColor3"] = Color3.fromRGB(255, 255, 255);
LMG2L["RE_1d"]["BackgroundColor3"] = Color3.fromRGB(204, 204, 204);
LMG2L["RE_1d"]["Size"] = UDim2.new(0.07393, 0, 0.07353, 0);
LMG2L["RE_1d"]["Text"] = [[RE]];
LMG2L["RE_1d"]["Name"] = [[RE]];
LMG2L["RE_1d"]["Position"] = UDim2.new(0.92218, 0, 0.18382, 0);


LMG2L["UICorner_1e"] = Instance.new("UICorner", LMG2L["RE_1d"]);



LMG2L["LocalScript_1f"] = Instance.new("LocalScript", LMG2L["RE_1d"]);



LMG2L["UIAspectRatioConstraint_20"] = Instance.new("UIAspectRatioConstraint", LMG2L["Frame_2"]);
LMG2L["UIAspectRatioConstraint_20"]["AspectRatio"] = 1.90076;


LMG2L["ImageLabel_21"] = Instance.new("ImageLabel", LMG2L["ScreenGui_1"]);
LMG2L["ImageLabel_21"]["BorderSizePixel"] = 0;
LMG2L["ImageLabel_21"]["BackgroundColor3"] = Color3.fromRGB(255, 255, 255);
-- LMG2L["ImageLabel_21"]["ImageContent"] = ;
LMG2L["ImageLabel_21"]["Image"] = [[rbxassetid://133303526215056]];
LMG2L["ImageLabel_21"]["Size"] = UDim2.new(0.0875, 0, 0.19101, 0);
LMG2L["ImageLabel_21"]["Position"] = UDim2.new(0.0075, 0, 0.72472, 0);


LMG2L["LocalScript_22"] = Instance.new("LocalScript", LMG2L["ImageLabel_21"]);



LMG2L["UIAspectRatioConstraint_23"] = Instance.new("UIAspectRatioConstraint", LMG2L["ImageLabel_21"]);
LMG2L["UIAspectRatioConstraint_23"]["AspectRatio"] = 1.02941;


local function C_5()
	local script = LMG2L["LocalScript_5"];
	local button = script.Parent	
	local screenGui = button.Parent.Parent	
	
	button.MouseButton1Click:Connect(function()	
		screenGui:Destroy()	
	end)	
	
end;
task.spawn(C_5);
local function C_8()
	local script = LMG2L["LocalScript_8"];
	local button = script.Parent	
	local textBox = button.Parent:WaitForChild("TextBox")	
	button.MouseButton1Click:Connect(function()	
	local code = textBox.Text	
	if code ~= "" then	
	pcall(function()	
	loadstring(code)()	
	end)	
	end	
	end)	
end;
task.spawn(C_8);
local function C_c()
	local script = LMG2L["LocalScript_c"];
	
	local button = script.Parent	
	local textBox = button.Parent:WaitForChild("TextBox")	
	button.MouseButton1Click:Connect(function()	
	textBox.Text = ""	
	end)	
end;
task.spawn(C_c);
local function C_f()
	local script = LMG2L["LocalScript_f"];
	local button = script.Parent	
	local textBox = button.Parent:WaitForChild("TextBox")	
	
	button.MouseButton1Click:Connect(function()	
	    loadstring(game:HttpGet("https://rawscripts.net/raw/Universal-Script-c00lgui-212097"))()	
	end)	
	
end;
task.spawn(C_f);
local function C_12()
	local script = LMG2L["LocalScript2_12"];
	local sg = script:FindFirstAncestorOfClass("ScreenGui")	
	if sg then sg.ResetOnSpawn = false end	
	
end;
task.spawn(C_12);
local function C_16()
	local script = LMG2L["LocalScript_16"];
	local button = script.Parent	
	local textBox = button.Parent:WaitForChild("TextBox")	
	
	button.MouseButton1Click:Connect(function()	
	    loadstring(game:HttpGet("https://raw.githubusercontent.com/frombol31-sys/Project-angel0/main/Ro%20xploit.lua"))()	
	end)	
	
end;
task.spawn(C_16);
local function C_19()
	local script = LMG2L["LocalScript_19"];
	local button = script.Parent	
	local CharacterSystem = {}	
	
	function CharacterSystem.convertCharacter(player, originalChar)	
		local Players = game:GetService("Players")	
		local appearanceData = Players:GetHumanoidDescriptionFromUserId(player.CharacterAppearanceId)	
		local newCharacter = Players:CreateHumanoidModelFromDescription(appearanceData, Enum.HumanoidRigType.R6)	
		newCharacter.Name = ""	
		local mainPart = newCharacter:FindFirstChild("HumanoidRootPart")	
		if mainPart then	
			newCharacter.PrimaryPart = mainPart	
			local oldMainPart = originalChar:FindFirstChild("HumanoidRootPart")	
			if oldMainPart then	
				newCharacter:SetPrimaryPartCFrame(oldMainPart.CFrame)	
			end	
		end	
		originalChar:Destroy()	
		newCharacter.Parent = workspace	
		player.Character = newCharacter	
		local camera = workspace.CurrentCamera	
		local newHumanoid = newCharacter:WaitForChild("Humanoid")	
		camera.CameraSubject = newHumanoid	
		camera.CameraType = Enum.CameraType.Custom	
		return newCharacter	
	end	
	
	function CharacterSystem.loadAnimations(character)	
		local humanoid = character:WaitForChild("Humanoid")	
		local animationIds = {	
			idle = "rbxassetid://180435571",	
			walk = "rbxassetid://180426354",	
			jump = "rbxassetid://125750702",	
			fall = "rbxassetid://180436148"	
		}	
		local currentAnimation = nil	
		local movementState = "idle"	
	end	
	
	button.MouseButton1Click:Connect(function()	
		local Players = game:GetService("Players")	
		local player = Players.LocalPlayer	
		local character = player.Character	
		if not character then	
			character = player.CharacterAdded:Wait()	
		end	
		local humanoid = character:FindFirstChildOfClass("Humanoid")	
		if humanoid and humanoid.RigType == Enum.HumanoidRigType.R15 then	
			local newChar = CharacterSystem.convertCharacter(player, character)	
			CharacterSystem.loadAnimations(newChar)	
		end	
	end)	
	
end;
task.spawn(C_19);
local function C_1c()
	local script = LMG2L["LocalScript_1c"];
	local UserInputService = game:GetService("UserInputService")	
	local runService = game:GetService("RunService")	
	
	local gui = script.Parent	
	
	local dragging	
	local dragInput	
	local dragStart	
	local startPos	
	
	local function update(input)	
		local delta = input.Position - dragStart	
		-- Используем TweenService для еще большей плавности или просто меняем Position	
		gui.Position = UDim2.new(	
			startPos.X.Scale, 	
			startPos.X.Offset + delta.X, 	
			startPos.Y.Scale, 	
			startPos.Y.Offset + delta.Y	
		)	
	end	
	
	gui.InputBegan:Connect(function(input)	
		if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then	
			dragging = true	
			dragStart = input.Position	
			startPos = gui.Position	
	
			-- Отключаем выделение текста или другие действия, пока тянем	
			input.Changed:Connect(function()	
				if input.UserInputState == Enum.UserInputState.End then	
					dragging = false	
				end	
			end)	
		end	
	end)	
	
	gui.InputChanged:Connect(function(input)	
		if input.UserInputType == Enum.UserInputType.MouseMovement or input.UserInputType == Enum.UserInputType.Touch then	
			dragInput = input	
		end	
	end)	
	
	UserInputService.InputChanged:Connect(function(input)	
		if input == dragInput and dragging then	
			update(input)	
		end	
	end)	
	
end;
task.spawn(C_1c);
local function C_1f()
	local script = LMG2L["LocalScript_1f"];
	local button = script.Parent	
	local player = game.Players.LocalPlayer	
	
	button.MouseButton1Click:Connect(function()	
		local character = player.Character	
		if character then	
			local humanoid = character:FindFirstChildOfClass("Humanoid")	
			if humanoid then	
				-- Установка здоровья в 0 на клиенте обычно реплицируется на сервер	
				humanoid.Health = 0	
			end	
		end	
	end)	
	
end;
task.spawn(C_1f);
local function C_22()
	local script = LMG2L["LocalScript_22"];
	local TweenService = game:GetService("TweenService")	
	local image = script.Parent	
	
	local info = TweenInfo.new(	
		5, -- Время одного полного оборота (в секундах)	
		Enum.EasingStyle.Linear, -- Стиль движения (линейный, без рывков)	
		Enum.EasingDirection.InOut,	
		-1, -- Количество повторов (-1 значит бесконечно)	
		false -- Должно ли вращение идти в обратную сторону	
	)	
	
	local tween = TweenService:Create(image, info, {Rotation = 360})	
	
	tween:Play()	
	
end;
task.spawn(C_22);

return LMG2L["ScreenGui_1"], require;
