% script to load, mask, save VideoClips or VideoClips_dB

clear
dirTop = '/Volumes/wehrlab/Rig4/Molly';
PATHout = [dirTop 'VideoClips_Light/'];

cd (PATHout)

load('lightvids.txt')   % this is a list of the VideoClips (that are all located in PATHout)

nClips = length(VideoClips);

nFramesEND = 26 *200;   % nframes after Land:seconds * fps
nFramesPre = 4 * 200;   % nframes before Land
nFrames = nFramesEND + nFramesPre;
for iClip  = 1:nClips
    tstart = tic;
    cd([dirTop 'save']);

    cd(VideoClips(iClip).dirName)

    fprintf('\nWorking on videoclip #%d\n',iClip)

    fprintf('Loading Seg, Circ\n')
    load('Segmentation');
    test = dir('Circ*.mat');
    load(test(1).name);

    fprintf('Reading frames\n')
    vr = VideoReader(VideoClips(iClip).vidName(1:end-1));
    % video might be too short?
    frameEND = min1([Seg.Land+nFramesEND vr.NumFrames]);
    frames = read(vr,[Seg.Land-nFramesPre frameEND]);

    % make mask and block out the laser indicator (...)
    fprintf('Making mask\n')
    xyr = [Circ.center; Circ.radius+40]';
    masksize =[1080 1440];
    [x, y] = meshgrid(1:masksize(2), 1:masksize(1));  %create pixel coordinates
    xyr = permute(xyr, [3 2 1]);  %move each circle along 3rd dimension
    mask = any(hypot(x - xyr(1, 1, :), y - xyr(1, 2, :)) <= xyr(1, 3, :), 3);
    %mask = any(bsxfun(@le, hypot(bsxfun(@minus, x, xyr(1, 1, :)),
    %bsxfun(@minus, y, xyr(1, 2, :))), xyr(1, 3, :)), 3); %(an alternative way)
    fprintf('masking\n')
    F = bsxfun(@times, frames, cast(mask,class(frames(:,:,:,1))) );

    % save as videoclip
    fprintf('Writing video\n')
    FNout = ['VideoClip' num2str(iClip)];
    vw = VideoWriter([PATHout FNout '.avi']);
    vw.FrameRate = vr.FrameRate;
    open(vw);
    writeVideo(vw,F);
    % close videoWriter
    clear vw
    % close videoReader
    clear vr
    clear mask frames F
    fprintf('done %3.1f \n\n',toc(tstart))
end     % iClip
